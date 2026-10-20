"""Generate review comments without changing Moodle's authoritative grades.

``blank_values`` contains ONLY teacher-declared score-cell tokens for unanswered
questions. Its default is empty. An empty score cell is missing evidence unless
``""`` is explicitly declared; a completed attempt does not make it a zero.
``absent_values`` applies to the status column and produces empty feedback.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import posixpath
import re
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import unquote, urlsplit


class FeedbackError(ValueError):
    """The requested output location cannot safely contain feedback files."""


_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _number(value):
    if isinstance(value, bool):
        raise ValueError("Una puntuación no puede ser un booleano.")
    try:
        result = Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError("Puntuación no numérica.") from None
    if not result.is_finite():
        raise ValueError("La puntuación debe ser finita.")
    return result


def _sentence(text):
    text = str(text).strip()
    return text if not text or text[-1] in ".!?…" else text + "."


def _check_question(question, source):
    number = question["number"]
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError("La numeración del modelo debe usar enteros positivos.")
    if question["type"] != source["type"]:
        raise ValueError("El tipo de pregunta del modelo no coincide con el snapshot.")
    originals = source.get("options", [])
    if source["type"] == "truefalse" and not originals:
        originals = [{"text": "Verdadero", "weight": 100 if source["true_answer"] else 0},
                     {"text": "Falso", "weight": 0 if source["true_answer"] else 100}]
    if originals:
        options = question.get("options", [])
        indices, labels = [], []
        for option in options:
            index = option["source_index"]
            label = option["label"]
            if (isinstance(index, bool) or not isinstance(index, int)
                    or not 0 <= index < len(originals)
                    or not isinstance(label, str) or not label):
                raise ValueError("Una opción del modelo tiene etiqueta o índice de origen inválido.")
            if (option["text"] != originals[index]["text"]
                    or _number(option["weight"]) != _number(originals[index]["weight"])):
                raise ValueError("Una opción del modelo no coincide con su índice en el snapshot.")
            indices.append(index)
            labels.append(label.upper())
        if set(indices) != set(range(len(originals))) or len(indices) != len(set(indices)) or len(labels) != len(set(labels)):
            raise ValueError("El modelo tiene opciones ausentes, duplicadas o etiquetas ambiguas.")
    if source["type"] == "numerical" and question.get("numerical") != source.get("numerical"):
        raise ValueError("Los criterios numéricos del modelo no coinciden con el snapshot.")


def _priority(config):
    result = {"max_concepts": 3, "marked_threshold": Decimal("0.5"), "min_evidence": 2}
    if not isinstance(config, dict) or set(config) - set(result):
        raise ValueError("feedback_priority admite max_concepts, marked_threshold y min_evidence.")
    result.update(config)
    for key in ("max_concepts", "min_evidence"):
        if type(result[key]) is not int or result[key] < 1:
            raise ValueError(f"{key} debe ser un entero positivo.")
    result["marked_threshold"] = _number(result["marked_threshold"])
    if not 0 <= result["marked_threshold"] <= 1:
        raise ValueError("marked_threshold debe estar entre 0 y 1.")
    return result


def _reference_key(path):
    """Compare snapshot declarations lexically; do not reopen mutable sources."""
    if not isinstance(path, str) or not path:
        raise ValueError("Un material declarado necesita una ruta no vacía.")
    parsed = urlsplit(unquote(unquote(path)))
    return parsed.scheme.lower(), parsed.netloc.lower(), posixpath.normpath(parsed.path)


def _material_access(metadata):
    if "materials" not in metadata:
        return None
    materials = metadata["materials"]
    if not isinstance(materials, dict):
        raise ValueError("materials debe ser un objeto de materiales declarados.")
    access_by_path = {}
    for item in materials.values():
        if not isinstance(item, dict) or item.get("access") not in ("estudiante", "docente"):
            raise ValueError("Un material declarado necesita access estudiante o docente.")
        key = _reference_key(item.get("path"))
        if key in access_by_path and access_by_path[key] != item["access"]:
            raise ValueError("Los materiales declaran accesos contradictorios para una misma ruta.")
        access_by_path[key] = item["access"]
    return access_by_path


def _student_references(detail, material_access=None):
    """Only emit explicitly student-accessible references with safe destinations."""
    references = detail.get("references", [])
    if not isinstance(references, list):
        raise ValueError("references debe ser una lista.")
    result = []
    for reference in references:
        if not isinstance(reference, dict):
            raise ValueError("Cada referencia debe ser un objeto.")
        if reference.get("access") != "estudiante":
            continue  # An absent or teacher access label never grants student access.
        title, path = reference.get("title"), reference.get("path")
        if not isinstance(title, str) or not title.strip() or not isinstance(path, str) or not path:
            raise ValueError("La referencia estudiantil necesita title y path.")
        decoded = unquote(unquote(path))
        if any(ord(char) < 32 for char in title + decoded) or any(char in decoded for char in "\\<>\""):
            raise ValueError("La referencia contiene caracteres inseguros.")
        parsed = urlsplit(decoded)
        if parsed.scheme:
            if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("La URL estudiantil debe ser HTTP(S), sin credenciales.")
        elif parsed.netloc or decoded.startswith("/") or not parsed.path:
            raise ValueError("La referencia debe usar una ruta relativa o una URL HTTP(S).")
        parts = parsed.path.split("/")
        if any(part in (".", "..") for part in parts) or "docente" in [part.casefold() for part in parts]:
            raise ValueError("La referencia estudiantil no puede salir de su raíz ni enlazar material docente reservado.")
        if material_access is not None:
            key = _reference_key(path)
            if key not in material_access:
                raise ValueError("La referencia estudiantil no corresponde a un material declarado.")
            if material_access[key] != "estudiante":
                raise ValueError("La referencia estudiantil contradice el acceso reservado del material declarado.")
        result.append(f"{title.strip()}: {path}")
    return result


def _conceptual(questions, scores, metadata, priorities=None):
    priorities = _priority(priorities or {})
    material_access = _material_access(metadata)
    missed = [q for q in questions if scores[str(q["number"])][0] is None
              or scores[str(q["number"])][0] < scores[str(q["number"])][1]]
    if not missed:
        return "Has alcanzado la puntuación máxima en los aspectos evaluados."
    concepts = OrderedDict()
    for question in questions:
        entry = metadata.get("questions", {}).get(question["source_id"], {})
        score, maximum = scores[str(question["number"])]
        for concept in dict.fromkeys(question.get("concepts", entry.get("concepts", []))):
            if not isinstance(concept, str) or not concept:
                raise ValueError("Los conceptos deben tener identificadores de texto no vacíos.")
            item = concepts.setdefault(concept, {"score": Decimal(0), "maximum": Decimal(0),
                                                "count": 0, "entries": []})
            item["score"] += score if score is not None else 0
            item["maximum"] += maximum
            item["count"] += 1
            if score is None or score < maximum:
                item["entries"].append(entry)
    selected = [(concept, value) for concept, value in concepts.items()
                if value["score"] < value["maximum"]]
    selected.sort(key=lambda item: (-(1 - item[1]["score"] / item[1]["maximum"]), -item[1]["count"]))
    parts = []
    for concept, value in selected[:priorities["max_concepts"]]:
        detail = metadata.get("concepts", {}).get(concept, {})
        label = detail.get("label") or concept
        marked = (value["score"] / value["maximum"] < priorities["marked_threshold"]
                  and value["count"] >= priorities["min_evidence"])
        prefix = "Dificultad acusada en" if marked else "Aspecto a revisar:"
        parts.append(_sentence(f"{prefix} {label}"))
        guidance = [detail.get("guidance")] + [entry.get("guidance") for entry in value["entries"]]
        parts.extend(_sentence(advice) for advice in dict.fromkeys(guidance) if advice)
        references = _student_references(detail, material_access)
        for entry in value["entries"]:
            references.extend(_student_references(entry, material_access))
        if references:
            parts.append("Material para repasar: " + "; ".join(dict.fromkeys(references)) + ".")
    if not selected:
        guidance = [metadata.get("questions", {}).get(question["source_id"], {}).get("guidance")
                    for question in missed]
        parts.append("Revisa los contenidos evaluados con puntuación inferior al máximo.")
        parts.extend(_sentence(advice) for advice in dict.fromkeys(guidance) if advice)
        if not any(guidance):
            parts.append("Los metadatos no incluyen orientaciones conceptuales específicas.")
    return " ".join(parts)


def _details(question, answer, source):
    """Describe only explicit selections and documented criteria, never regrade."""
    prefix = f"Pregunta {question['number']}. "
    options = question.get("options", [])
    if options:
        labels = [item.strip().upper() for item in re.split(r"[,;|\s]+", answer.strip())
                  if item.strip()]
        by_label = {str(option["label"]).upper(): option for option in options}
        if not labels or any(label not in by_label for label in labels):
            return None
        original_options = source.get("options", [])
        parts = []
        for label in dict.fromkeys(labels):
            option = by_label[label]
            weight = _number(option["weight"])
            verdict = ("correcta" if weight == 100 else "con crédito parcial"
                       if weight > 0 else "sin crédito" if weight == 0
                       else "con penalización")
            part = f"Selección {label}: {verdict}."
            index = option.get("source_index")
            original = original_options[index] if (isinstance(index, int)
                       and not isinstance(index, bool)
                       and 0 <= index < len(original_options)) else {}
            feedback = original.get("feedback")
            if feedback:
                part += " " + _sentence(feedback)
            parts.append(part)
        return prefix + " ".join(parts)
    if question.get("type") == "numerical":
        try:
            _number(answer)
        except ValueError:
            return None
        criteria = []
        for item in question.get("numerical", source.get("numerical", [])):
            if _number(item.get("weight", 100)) <= 0:
                continue
            if "min" in item and "max" in item:
                criteria.append(f"intervalo [{item['min']}, {item['max']}]")
            elif "value" in item:
                criteria.append(f"valor {item['value']} con tolerancia {item.get('tolerance', 0)}")
        if criteria:
            return prefix + f"Respuesta registrada: {answer}. Criterios del banco: " + "; ".join(criteria) + "."
    return None


def _read_csv(path, delimiter):
    raw = path.read_bytes().decode("utf-8-sig")
    if not raw:
        raise ValueError("El CSV está vacío.")
    if delimiter is None:
        # Sniffer's frequency heuristic can fail on quoted delimiters, decimal
        # commas, or multiline comments. Require an unambiguous parsed table.
        candidates = []
        for candidate in (",", ";", "\t"):
            try:
                table = list(csv.reader(io.StringIO(raw, newline=""),
                                        delimiter=candidate, strict=True))
                if table and len(table[0]) > 1 and all(len(row) == len(table[0]) for row in table):
                    candidates.append(candidate)
            except csv.Error:
                continue
        if len(candidates) != 1:
            raise ValueError("No se pudo detectar un delimitador único; decláralo en la configuración.")
        delimiter = candidates[0]
    if delimiter not in (",", ";", "\t"):
        raise ValueError("El delimitador debe ser coma, punto y coma o tabulador.")
    try:
        dialect = csv.Sniffer().sniff(raw[:65536], delimiters=delimiter)
    except csv.Error:
        dialect = csv.excel
    formatting = {"delimiter": delimiter or dialect.delimiter,
                  "quotechar": dialect.quotechar or '"',
                  "doublequote": dialect.doublequote if dialect.escapechar else True,
                  "escapechar": dialect.escapechar,
                  "quoting": dialect.quoting,
                  "lineterminator": "\r\n" if "\r\n" in raw else "\n"}
    reader = csv.reader(io.StringIO(raw, newline=""), strict=True,
                        **{key: value for key, value in formatting.items() if key != "lineterminator"})
    header = next(reader, None)
    if not header or len(header) != len(set(header)) or any(not value for value in header):
        raise ValueError("Las cabeceras deben ser únicas y no estar vacías.")
    rows = []
    for values in reader:
        if not values:
            raise ValueError("El CSV contiene una fila vacía sin identificador.")
        if len(values) != len(header):
            raise ValueError(f"La fila que termina en la línea {reader.line_num} no coincide con las cabeceras.")
        rows.append((reader.line_num, values))
    return header, rows, formatting


def _write_report(output, report):
    for suffix in range(1, 100000):
        path = output / ("feedback-report.json" if suffix == 1 else f"feedback-report-{suffix}.json")
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            return
        except FileExistsError:
            continue
        except OSError as exc:
            raise FeedbackError(f"No se pudo guardar el informe en {output}: {exc}") from exc
    raise FeedbackError("No queda un nombre libre para el informe de feedback.")


def build_feedback(manifest_path, input_paths, config_path, output_dir, *,
                   detailed=False, consolidated=False, gradebook_path=None):
    """Return an audit report and write only fully validated UTF-8-BOM CSVs.

    Any ambiguous input blocks every CSV in this batch. Existing CSVs also block
    the batch; reports receive a free numbered filename. Scores, row order and
    unrelated cells are never normalized or recalculated. Detailed feedback is
    opt-in and requires explicit answer columns; unavailable individual answers
    receive conceptual feedback and an audit warning, not an invented selection.
    """
    output = Path(output_dir).expanduser().resolve()
    if output == _PACKAGE_ROOT or _PACKAGE_ROOT in output.parents:
        raise FeedbackError("La salida debe estar fuera del paquete instalado.")
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise FeedbackError(f"No se puede crear la carpeta de salida: {exc}") from exc
    report = {"status": "blocked", "outputs": [], "incidents": [], "audit": [],
              "students": {"read": 0, "absent": 0, "with_feedback": 0},
              "manifest_sha256": None}

    def incident(code, message, level="error", **context):
        report["incidents"].append({"code": code, "level": level, "message": message, **context})

    def blocked():
        return any(item["level"] == "error" for item in report["incidents"])

    def finish():
        report["status"] = "blocked" if blocked() else "ok"
        _write_report(output, report)
        return report

    try:
        manifest_file = Path(manifest_path).expanduser().resolve()
        manifest_bytes = manifest_file.read_bytes()
        report["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
        config = json.loads(Path(config_path).read_text(encoding="utf-8-sig"))
        if not isinstance(manifest, dict) or not isinstance(config, dict):
            raise ValueError("El manifiesto y la configuración deben ser objetos JSON.")
        if manifest.get("schema_version") != 1 or config.get("schema_version", 1) != 1:
            raise ValueError("Versión de contrato no compatible.")
        snapshot_relative = Path(manifest["bank_snapshot"])
        if snapshot_relative.is_absolute() or ".." in snapshot_relative.parts:
            raise ValueError("El snapshot debe usar una ruta relativa dentro de la carpeta del manifiesto.")
        snapshot = (manifest_file.parent / snapshot_relative).resolve()
        if manifest_file.parent not in snapshot.parents:
            raise ValueError("El snapshot se resuelve fuera de la carpeta del manifiesto.")
        snapshot_bytes = snapshot.read_bytes()
        if hashlib.sha256(snapshot_bytes).hexdigest() != manifest.get("bank_sha256"):
            incident("SNAPSHOT_HASH_MISMATCH", "La huella del banco snapshot no coincide con el manifiesto.")
            return finish()
        from .gift import parse_gift
        source_questions = parse_gift(snapshot_bytes.decode("utf-8-sig"))
        source_by_id = {question["id"]: question for question in source_questions}
        if len(source_by_id) != len(source_questions):
            raise ValueError("El snapshot contiene identificadores de pregunta duplicados.")
        models = {}
        for model in manifest["models"]:
            model_id = model["id"]
            if not isinstance(model_id, str) or not model_id.strip() or model_id in models:
                raise ValueError("El manifiesto contiene un modelo vacío o duplicado.")
            questions = model["questions"]
            numbers = [str(question["number"]) for question in questions]
            if not questions or len(set(numbers)) != len(numbers):
                raise ValueError("El modelo contiene numeración vacía o duplicada.")
            if any(question["source_id"] not in source_by_id for question in questions):
                raise ValueError("Una pregunta del modelo no existe en el snapshot.")
            for question in questions:
                _check_question(question, source_by_id[question["source_id"]])
            models[model_id] = model
        if not models:
            raise ValueError("El manifiesto no contiene modelos.")
        metadata = manifest.get("metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("Los metadatos deben ser un objeto JSON.")
        required_columns = ["identifier_column", "model_column", "status_column"]
        if gradebook_path is None:
            required_columns.append("feedback_column")
        for name in required_columns:
            if not isinstance(config.get(name), str) or not config[name]:
                raise ValueError(f"Falta la columna explícita {name} en la configuración.")
        fixed_columns = [config[name] for name in required_columns]
        if len(set(fixed_columns)) != len(fixed_columns):
            raise ValueError("Identificador, modelo, estado y comentario deben usar columnas distintas.")
        for name in ("absent_values", "blank_values"):
            if not isinstance(config.get(name, []), list) or any(not isinstance(token, str) for token in config.get(name, [])):
                raise ValueError(f"{name} debe ser una lista de textos explícitos.")
        priorities = _priority(config.get("feedback_priority", {}))
        gradebook = None
        if gradebook_path is not None:
            gradebook = config.get("gradebook")
            if not isinstance(gradebook, dict) or set(gradebook) - {
                    "identifier_column", "feedback_column", "grade_column",
                    "model_column", "default_model", "delimiter"}:
                raise ValueError("Se requiere un perfil gradebook explícito con columnas y modelo.")
            book_columns = []
            for name in ("identifier_column", "feedback_column", "grade_column"):
                if not isinstance(gradebook.get(name), str) or not gradebook[name]:
                    raise ValueError(f"Falta gradebook.{name}.")
                book_columns.append(gradebook[name])
            if ("model_column" in gradebook) == ("default_model" in gradebook):
                raise ValueError("gradebook debe declarar exactamente model_column o default_model.")
            if "model_column" in gradebook:
                if not isinstance(gradebook["model_column"], str) or not gradebook["model_column"]:
                    raise ValueError("gradebook.model_column debe ser texto no vacío.")
                book_columns.append(gradebook["model_column"])
            elif gradebook["default_model"] not in models:
                raise ValueError("El modelo predeterminado del libro no pertenece al manifiesto.")
            if len(book_columns) != len(set(book_columns)):
                raise ValueError("Las columnas del libro deben ser distintas.")
        if not isinstance(config.get("models", {}), dict):
            raise ValueError("models en configuración debe ser un mapa por identificador.")
        if set(config.get("models", {})) - set(models):
            raise ValueError("La configuración contiene un modelo desconocido.")
        mappings = {}
        for model_id, model in models.items():
            override = config.get("models", {}).get(model_id, {})
            if not isinstance(override, dict):
                raise ValueError("La configuración específica del modelo debe ser un objeto.")
            maps = {key: override.get(key, config.get(key, {})) for key in
                    ("question_columns", "max_scores", "answer_columns")}
            if any(not isinstance(value, dict) for value in maps.values()):
                raise ValueError("Las columnas de preguntas, respuestas y máximos deben ser mapas.")
            numbers = [str(question["number"]) for question in model["questions"]]
            for number in numbers:
                if not isinstance(maps["question_columns"].get(number), str) or not maps["question_columns"][number]:
                    raise ValueError(f"Falta el mapeo de puntuación para modelo {model_id}, pregunta {number}.")
                if number not in maps["max_scores"] or _number(maps["max_scores"][number]) <= 0:
                    raise ValueError(f"Falta un máximo positivo para modelo {model_id}, pregunta {number}.")
                if detailed and (not isinstance(maps["answer_columns"].get(number), str) or not maps["answer_columns"][number]):
                    raise ValueError(f"El detalle requiere answer_columns para modelo {model_id}, pregunta {number}.")
            score_columns = [maps["question_columns"][number] for number in numbers]
            if len(set(score_columns)) != len(score_columns) or set(score_columns) & set(fixed_columns):
                raise ValueError("Las columnas de puntuación deben ser distintas entre sí y de las columnas de control.")
            if detailed:
                answer_columns = [maps["answer_columns"][number] for number in numbers]
                if len(set(answer_columns)) != len(answer_columns) or set(answer_columns) & (set(score_columns) | set(fixed_columns)):
                    raise ValueError("Las columnas de respuestas deben ser distintas de las demás columnas configuradas.")
            mappings[model_id] = maps
        if isinstance(input_paths, (str, Path)):
            raise ValueError("input_paths debe ser una lista de archivos CSV.")
        paths = [Path(path).expanduser().resolve() for path in input_paths]
        if not paths or len(set(paths)) != len(paths):
            raise ValueError("Se requiere una lista no vacía de archivos CSV sin duplicados.")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError) as exc:
        incident("INVALID_INPUT", str(exc))
        return finish()

    groups, all_rows, seen_identifiers, feedback_by_key = OrderedDict(), [], set(), {}
    absent_values, blank_values = set(config.get("absent_values", [])), set(config.get("blank_values", []))
    for path in paths:
        try:
            header, rows, formatting = _read_csv(path, config.get("delimiter"))
        except (OSError, ValueError, UnicodeError, csv.Error) as exc:
            incident("INVALID_CSV", str(exc), file=path.name)
            continue
        missing = [column for column in fixed_columns if column not in header]
        if missing:
            incident("MISSING_COLUMN", "Faltan columnas de control: " + ", ".join(missing), file=path.name)
            continue
        positions = {column: index for index, column in enumerate(header)}
        for line, cells in rows:
            report["students"]["read"] += 1
            context = {"file": path.name, "row": line}
            raw_identifier = cells[positions[config["identifier_column"]]]
            identifier = raw_identifier.strip()
            model_id = cells[positions[config["model_column"]]]
            if not identifier:
                incident("MISSING_IDENTIFIER", "La fila no tiene identificador; no se atribuye un resultado.", **context)
                continue
            if gradebook is not None and identifier != raw_identifier:
                incident("INVALID_IDENTIFIER", "El identificador tiene espacios externos; confirma la correspondencia exacta.", **context)
                continue
            identity_key = (identifier, model_id) if gradebook is not None else identifier
            if identity_key in seen_identifiers:
                incident("DUPLICATE_IDENTIFIER", "Identificador repetido entre filas, archivos o modelos; requiere revisión.", **context)
                continue
            seen_identifiers.add(identity_key)
            if model_id not in models:
                incident("UNKNOWN_MODEL", "El modelo de la fila no coincide con el manifiesto.", **context)
                continue
            context["model"] = model_id
            model, maps = models[model_id], mappings[model_id]
            required = [maps["question_columns"][str(q["number"])] for q in model["questions"]]
            if detailed:
                required.extend(maps["answer_columns"][str(q["number"])] for q in model["questions"])
            missing = [column for column in required if column not in positions]
            if missing:
                incident("MISSING_COLUMN", "Faltan columnas configuradas: " + ", ".join(missing), **context)
                continue
            if gradebook is None and model_id in groups and (
                    groups[model_id]["header"] != header or groups[model_id]["formatting"] != formatting):
                incident("INCOMPATIBLE_CSV", "El mismo modelo usa columnas o dialectos incompatibles entre archivos.", **context)
                continue
            groups.setdefault(model_id, {"header": header, "formatting": formatting, "rows": []})
            if cells[positions[config["status_column"]]] in absent_values:
                feedback = ""
                report["students"]["absent"] += 1
            else:
                scores, valid_row = {}, True
                for question in model["questions"]:
                    number = str(question["number"])
                    raw = cells[positions[maps["question_columns"][number]]]
                    maximum = _number(maps["max_scores"][number])
                    if raw in blank_values:
                        score = None
                    elif not raw.strip():
                        incident("MISSING_SCORE", "Puntuación vacía no declarada como respuesta en blanco; falta evidencia.", question=number, **context)
                        valid_row = False
                        continue
                    else:
                        try:
                            score = _number(raw)
                        except ValueError:
                            incident("INVALID_SCORE", "La puntuación no es numérica ni un token explícito de respuesta en blanco.", question=number, **context)
                            valid_row = False
                            continue
                        if score > maximum:
                            incident("SCORE_EXCEEDS_MAXIMUM", "La puntuación supera el máximo configurado; revisar el mapeo.", question=number, **context)
                            valid_row = False
                            continue
                    scores[number] = score, maximum
                if not valid_row:
                    continue
                try:
                    feedback = _conceptual(model["questions"], scores, metadata, priorities)
                    if detailed:
                        for question in model["questions"]:
                            number = str(question["number"])
                            answer = cells[positions[maps["answer_columns"][number]]]
                            detail = _details(question, answer, source_by_id[question["source_id"]]) if answer.strip() else None
                            if detail:
                                feedback += " " + detail
                            else:
                                incident("DETAIL_UNAVAILABLE", "No hay selección interpretable o criterio documentado para detallar esta respuesta; se conserva la orientación conceptual.", level="warning", question=number, **context)
                except (KeyError, TypeError, ValueError, AttributeError) as exc:
                    incident("INVALID_METADATA", "No se pudo generar feedback con los metadatos: " + str(exc), **context)
                    continue
                report["students"]["with_feedback"] += 1
            result = list(cells)
            if gradebook is None:
                result[positions[config["feedback_column"]]] = feedback
            feedback_by_key[(identifier, model_id)] = feedback
            groups[model_id]["rows"].append(result)
            all_rows.append((header, formatting, result))

    if not report["students"]["read"]:
        incident("NO_STUDENTS", "No hay filas de estudiantes para procesar.")
    if gradebook is not None:
        try:
            gradebook_file = Path(gradebook_path).expanduser().resolve()
            header, rows, formatting = _read_csv(gradebook_file, gradebook.get("delimiter"))
            report["gradebook_sha256"] = hashlib.sha256(gradebook_file.read_bytes()).hexdigest()
            if not rows:
                raise ValueError("El libro de calificaciones no contiene filas.")
            if any(column not in header for column in book_columns):
                raise ValueError("Faltan columnas declaradas del libro de calificaciones.")
            positions = {column: index for index, column in enumerate(header)}
            groups, all_rows, found = OrderedDict(), [], set()
            for line, cells in rows:
                raw_identifier = cells[positions[gradebook["identifier_column"]]]
                identifier = raw_identifier.strip()
                model_id = (cells[positions[gradebook["model_column"]]]
                            if "model_column" in gradebook else gradebook["default_model"])
                key = (identifier, model_id)
                if not identifier:
                    incident("MISSING_IDENTIFIER", "Fila del libro sin identificador.", row=line)
                    continue
                if identifier != raw_identifier:
                    incident("INVALID_IDENTIFIER", "El identificador del libro tiene espacios externos; confirma la correspondencia exacta.", row=line)
                    continue
                if key in found:
                    incident("DUPLICATE_GRADEBOOK_IDENTIFIER", "Fila repetida en el libro para el mismo identificador y modelo.", row=line)
                    continue
                found.add(key)
                if model_id not in models:
                    incident("UNKNOWN_MODEL", "Modelo del libro desconocido o vacío; no se atribuye por intuición.", row=line)
                    continue
                result = list(cells)
                if key in feedback_by_key:
                    before = result[positions[gradebook["feedback_column"]]]
                    result[positions[gradebook["feedback_column"]]] = feedback_by_key[key]
                    report["audit"].append({"identifier": identifier, "model": model_id,
                                            "before": before, "after": feedback_by_key[key],
                                            "grade_preserved": cells[positions[gradebook["grade_column"]]]})
                else:
                    incident("NO_DETAIL", "Fila conservada: no hay detalle por pregunta para este participante y modelo.",
                             level="warning", row=line, model=model_id)
                groups.setdefault(model_id, {"header": header, "formatting": formatting, "rows": []})["rows"].append(result)
                all_rows.append((header, formatting, result))
            for identifier, model_id in feedback_by_key.keys() - found:
                incident("UNMATCHED_DETAIL", "Un resultado detallado no tiene correspondencia en el libro.",
                         identifier=identifier, model=model_id)
            paths.append(gradebook_file)
        except (OSError, ValueError, TypeError, KeyError, UnicodeError, csv.Error) as exc:
            incident("INVALID_GRADEBOOK", str(exc))
    targets = []
    for model_id, group in groups.items():
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", model_id)
        targets.append((output / f"modelo_{safe_id}_CORREGIDO.csv", group))
    if consolidated and all_rows:
        header, formatting, _ = all_rows[0]
        if any(other_header != header or other_format != formatting for other_header, other_format, _ in all_rows):
            incident("INCOMPATIBLE_CONSOLIDATION", "El consolidado requiere las mismas columnas, orden y dialecto en todos los CSV.")
        else:
            targets.append((output / "CONSOLIDADO_CORREGIDO.csv", {
                "header": header, "formatting": formatting, "rows": [row for _, _, row in all_rows]}))
    names = [path.name.casefold() for path, _ in targets]
    if len(names) != len(set(names)):
        incident("OUTPUT_NAME_COLLISION", "Los modelos generan nombres de archivo equivalentes.")
    for path, _ in targets:
        if path.exists() or path.is_symlink():
            incident("OUTPUT_EXISTS", "Ya existe el archivo de salida; no se sobrescribe.", file=path.name)
        if path in paths or path in (manifest_file, snapshot, Path(config_path).resolve()):
            incident("OUTPUT_IS_INPUT", "Una salida coincide con un archivo de entrada; no se modifica.", file=path.name)
    if blocked():
        return finish()
    created = []
    try:
        for path, group in targets:
            with path.open("x", encoding="utf-8-sig", newline="") as stream:
                created.append(path)
                writer = csv.writer(stream, **group["formatting"])
                writer.writerow(group["header"])
                writer.writerows(group["rows"])
        report["outputs"] = [str(path) for path in created]
    except (OSError, csv.Error) as exc:
        for path in created:
            path.unlink(missing_ok=True)
        incident("WRITE_FAILED", "No se exporta el lote: " + str(exc))
    return finish()
