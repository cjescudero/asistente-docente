"""Validate an evidence-based evaluation and prepare a copy for manual Moodle import.

The agent/teacher assesses submissions. This module only checks the assessment,
computes the declared weighted grade, and joins exact identifiers. It never
opens or executes student submissions and never modifies the downloaded CSV.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path, PureWindowsPath

from .feedback import _PACKAGE_ROOT, _number, _read_csv


class GradingError(ValueError):
    """The requested output directory cannot safely receive assessment results."""


_ROUNDING = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN, "down": ROUND_DOWN}
_STATUSES = {"evaluated", "absent", "unreadable", "pending"}


def _object(value, required, optional=(), *, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} debe ser un objeto JSON.")
    missing, extra = set(required) - value.keys(), value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f"{label}: campos ausentes {sorted(missing)}; campos desconocidos {sorted(extra)}.")
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} debe ser un texto no vacío.")
    return value


def _identifier(value, label):
    _text(value, label)
    if value != value.strip():
        raise ValueError(f"{label} tiene espacios externos; confirma el identificador exacto.")
    return value


def _write_report(output, report):
    for suffix in range(1, 100000):
        path = output / ("grading-report.json" if suffix == 1 else f"grading-report-{suffix}.json")
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            return
        except FileExistsError:
            continue
        except OSError as exc:
            raise GradingError(f"No se pudo guardar el informe de evaluación: {exc}") from exc
    raise GradingError("No queda un nombre libre para el informe de evaluación.")


def _validate_config(config):
    _object(config, ("schema_version", "profile", "activity_id", "attempt_id",
                     "identifier_column", "grade_column", "feedback_column",
                     "grade_max", "decimals", "rounding"),
            ("delimiter", "decimal_separator", "advanced_grading",
             "activity_column", "attempt_column", "activity_record"), label="Perfil Moodle")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("Versión de perfil Moodle no compatible.")
    if config["profile"] not in ("worksheet", "gradebook"):
        raise ValueError("profile debe ser worksheet o gradebook.")
    for name in ("activity_id", "attempt_id"):
        _identifier(config[name], name)
    columns = []
    for name in ("identifier_column", "grade_column", "feedback_column", "activity_column", "attempt_column"):
        if name in config:
            columns.append(_text(config[name], name))
    if len(columns) != len(set(columns)):
        raise ValueError("Las columnas configuradas deben ser distintas.")
    if _number(config["grade_max"]) <= 0:
        raise ValueError("grade_max debe ser positivo; esta versión admite escalas numéricas desde cero.")
    if type(config["decimals"]) is not int or not 0 <= config["decimals"] <= 8:
        raise ValueError("decimals debe ser un entero entre 0 y 8.")
    try:
        maximum = _number(config["grade_max"])
        if maximum.quantize(Decimal(1).scaleb(-config["decimals"])) != maximum:
            raise ValueError("grade_max no se puede representar con los decimales declarados.")
    except ArithmeticError:
        raise ValueError("grade_max no se puede representar con los decimales declarados.") from None
    if config["rounding"] not in _ROUNDING:
        raise ValueError("rounding debe ser half_up, half_even o down.")
    if config.get("decimal_separator", ".") not in (".", ","):
        raise ValueError("decimal_separator debe ser punto o coma.")
    if "advanced_grading" in config and type(config["advanced_grading"]) is not bool:
        raise ValueError("advanced_grading debe ser un booleano.")
    if config["profile"] == "worksheet" and "advanced_grading" not in config:
        raise ValueError("El perfil worksheet debe declarar advanced_grading explícitamente.")
    if "activity_record" in config:
        _text(config["activity_record"], "activity_record")


def _activity_record(evaluation, config, config_file):
    """Bind to explicit activity identity/version and hash registered teacher files.

    This is provenance validation, not an interpretation of Markdown criteria.
    A known course root also prevents following symlinks outside that root.
    """
    from .project import find_project
    course_root = find_project(config_file.parent)

    def document(base, relative):
        _text(relative, "Ruta de documento de actividad")
        if Path(relative).is_absolute() or PureWindowsPath(relative).is_absolute() or "\\" in relative:
            raise ValueError("Los documentos de actividad deben usar rutas relativas portables.")
        resolved = (base / relative).resolve()
        if course_root is not None and (resolved == course_root or course_root not in resolved.parents):
            raise ValueError("El registro o un documento de actividad sale de la raíz del curso, también mediante enlaces.")
        if not resolved.is_file():
            raise ValueError(f"No existe un archivo regular para el documento registrado: {relative}.")
        return resolved

    registry_path = document(config_file.parent, config["activity_record"])
    content = registry_path.read_bytes()
    record = json.loads(content.decode("utf-8-sig"))
    if not isinstance(record, dict) or type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        raise ValueError("El registro de actividad debe usar schema_version: 1.")
    _identifier(record.get("id"), "Identificador del registro de actividad")
    _text(record.get("version"), "Versión del registro de actividad")
    _text(evaluation.get("activity_version"), "activity_version de la evaluación")
    if record["id"] != evaluation["activity_id"] or record["version"] != evaluation["activity_version"]:
        raise ValueError("La identidad o versión de la actividad no coincide con el registro utilizado para corregir.")
    files = record.get("files")
    if not isinstance(files, dict):
        raise ValueError("El registro de actividad necesita files.")
    required = [("statement", files.get("statement"), "estudiante"), ("rubric", files.get("rubric"), "docente")]
    if "teaching_guide" in files:
        required.append(("teaching_guide", files["teaching_guide"], "docente"))
    templates = files.get("templates", [])
    if not isinstance(templates, list):
        raise ValueError("files.templates debe ser una lista.")
    required.extend((f"templates[{index}]", item, "estudiante") for index, item in enumerate(templates))
    documents = {}
    for label, item, audience in required:
        if not isinstance(item, dict) or item.get("audience") != audience:
            raise ValueError(f"El documento {label} necesita la audiencia {audience}.")
        path = document(registry_path.parent, item.get("path"))
        documents[label] = {"path": item["path"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "audience": audience}
        if "pdf" in item:
            pdf_path = document(registry_path.parent, item["pdf"])
            documents[label + ".pdf"] = {"path": item["pdf"],
                                         "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                                         "audience": audience}
    return {"id": record["id"], "version": record["version"],
            "path": config["activity_record"], "sha256": hashlib.sha256(content).hexdigest(),
            "documents": documents, "course_boundary_checked": course_root is not None}


def _rubric(evaluation):
    _object(evaluation, ("schema_version", "activity_id", "attempt_id", "rubric", "evaluations"),
            ("activity_version", "sources"), label="Evaluación")
    if type(evaluation["schema_version"]) is not int or evaluation["schema_version"] != 1:
        raise ValueError("Versión de evaluación no compatible.")
    for name in ("activity_id", "attempt_id"):
        _identifier(evaluation[name], name)
    if "activity_version" in evaluation:
        _text(evaluation["activity_version"], "activity_version")
    if "sources" in evaluation and (not isinstance(evaluation["sources"], list)
                                   or any(not isinstance(item, str) or not item.strip()
                                          for item in evaluation["sources"])):
        raise ValueError("sources debe ser una lista de localizadores de los criterios docentes.")
    if not isinstance(evaluation["rubric"], list) or not evaluation["rubric"]:
        raise ValueError("Se necesita una rúbrica no vacía para calcular notas.")
    criteria = {}
    for item in evaluation["rubric"]:
        _object(item, ("id", "max_score", "weight"), ("label",), label="Criterio")
        identifier = _identifier(item["id"], "Identificador de criterio")
        if identifier in criteria:
            raise ValueError("La rúbrica contiene criterios repetidos.")
        maximum, weight = _number(item["max_score"]), _number(item["weight"])
        if maximum <= 0 or weight <= 0:
            raise ValueError("Máximos y pesos de criterios deben ser positivos.")
        criteria[identifier] = (maximum, weight)
    if sum(weight for _, weight in criteria.values()) != 100:
        raise ValueError("Los pesos de la rúbrica deben sumar exactamente 100.")
    if not isinstance(evaluation["evaluations"], list) or not evaluation["evaluations"]:
        raise ValueError("evaluations debe ser una lista no vacía.")
    return criteria


def _assessment(entry, rubric, config):
    _object(entry, ("status", "justification"),
            ("student_id", "group_id", "members", "criteria", "feedback", "total_points"),
            label="Valoración")
    individual = "student_id" in entry
    if individual:
        if "group_id" in entry or "members" in entry:
            raise ValueError("La valoración debe ser individual o de un grupo explícito.")
        members = [_identifier(entry["student_id"], "student_id")]
    else:
        _identifier(entry.get("group_id"), "group_id")
        members = entry.get("members")
        if not isinstance(members, list) or not members:
            raise ValueError("El grupo debe declarar sus identificadores de miembros.")
        for member in members:
            _identifier(member, "Identificador de miembro")
        if len(set(members)) != len(members):
            raise ValueError("Un grupo contiene miembros repetidos.")
    status = entry["status"]
    if status not in _STATUSES:
        raise ValueError("Estado de valoración desconocido.")
    _text(entry["justification"], "Justificación")
    if status != "evaluated":
        if entry.get("criteria") or "total_points" in entry:
            raise ValueError("Una entrega pendiente, ausente o ilegible no puede incluir puntuaciones.")
        if "feedback" in entry and not isinstance(entry["feedback"], str):
            raise ValueError("feedback debe ser texto.")
        return members, None
    _text(entry.get("feedback"), "Feedback para el estudiante")
    items = entry.get("criteria")
    if not isinstance(items, list) or not items:
        raise ValueError("La valoración evaluada debe incluir evidencias y puntuaciones por criterio.")
    by_id, points, weighted = {}, Decimal(0), Decimal(0)
    for item in items:
        _object(item, ("id", "score", "evidence"), label="Valoración de criterio")
        identifier = _identifier(item["id"], "Identificador de criterio")
        if identifier not in rubric or identifier in by_id:
            raise ValueError("La valoración contiene un criterio desconocido o duplicado.")
        score = _number(item["score"])
        maximum, weight = rubric[identifier]
        if not 0 <= score <= maximum:
            raise ValueError("La puntuación de un criterio queda fuera de su intervalo.")
        evidence = item["evidence"]
        if (not isinstance(evidence, list) or not evidence
                or any(not isinstance(text, str) or not text.strip() for text in evidence)):
            raise ValueError("Cada criterio necesita evidencias textuales no vacías con su localización.")
        by_id[identifier] = item
        points += score
        weighted += score / maximum * weight
    if set(by_id) != set(rubric):
        raise ValueError("Faltan criterios de la rúbrica en la valoración.")
    if "total_points" in entry and _number(entry["total_points"]) != points:
        raise ValueError("total_points no coincide con la suma de puntuaciones por criterio.")
    grade = weighted / 100 * _number(config["grade_max"])
    rounded = grade.quantize(Decimal(1).scaleb(-config["decimals"]),
                             rounding=_ROUNDING[config["rounding"]])
    if not 0 <= rounded <= _number(config["grade_max"]):
        raise ValueError("La nota redondeada queda fuera de la escala declarada.")
    text = format(rounded, f".{config['decimals']}f")
    if config.get("decimal_separator", ".") == ",":
        text = text.replace(".", ",")
    return members, {"grade": text, "points": str(points), "weighted_percent": str(weighted),
                     "unrounded_grade": str(grade)}


def export_grades(evaluation_path, input_path, config_path, output_dir):
    """Prepare one worksheet/gradebook copy, or only a report when validation fails.

    All identifiers must match exactly. ``activity_id`` and ``attempt_id`` bind
    the whole batch; optional CSV columns filter matching rows while preserving
    every row. Group members are expanded explicitly. Existing files are never
    overwritten. Pending/absent/unreadable assessments leave both cells intact.
    """
    output = Path(output_dir).expanduser().resolve()
    if output == _PACKAGE_ROOT or _PACKAGE_ROOT in output.parents:
        raise GradingError("La salida debe estar fuera del paquete instalado.")
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise GradingError(f"No se puede crear la carpeta de salida: {exc}") from exc
    report = {"status": "blocked", "outputs": [], "incidents": [], "audit": [],
              "evaluation": None, "input_sha256": {}, "rows": 0, "updated": 0}

    def incident(code, message, level="error", **context):
        report["incidents"].append({"code": code, "message": message, "level": level, **context})

    def blocked():
        return any(item["level"] == "error" for item in report["incidents"])

    def finish():
        report["status"] = "blocked" if blocked() else "ok"
        _write_report(output, report)
        return report

    try:
        evaluation_file, input_file, config_file = [
            Path(path).expanduser().resolve() for path in (evaluation_path, input_path, config_path)]
        for label, path in (("evaluation", evaluation_file), ("moodle", input_file), ("config", config_file)):
            report["input_sha256"][label] = hashlib.sha256(path.read_bytes()).hexdigest()
        evaluation = json.loads(evaluation_file.read_text(encoding="utf-8-sig"))
        report["evaluation"] = evaluation
        config = json.loads(config_file.read_text(encoding="utf-8-sig"))
        _validate_config(config)
        rubric = _rubric(evaluation)
        if any(evaluation[name] != config[name] for name in ("activity_id", "attempt_id")):
            raise ValueError("La actividad o convocatoria de la evaluación no coincide con el perfil Moodle.")
        if "activity_record" in config:
            report["activity_record"] = _activity_record(evaluation, config, config_file)
            if not report["activity_record"]["course_boundary_checked"]:
                incident("COURSE_BOUNDARY_UNVERIFIED",
                         "No se encontró proyecto-docente.json en los antecesores del perfil. "
                         "Se comprobaron archivos y versiones, pero no el confinamiento a una raíz de curso.",
                         "warning")
        else:
            incident("ACTIVITY_RECORD_UNVERIFIED",
                     "Sin activity_record: se comprobaron actividad y convocatoria del lote, "
                     "pero no la versión ni los documentos de un registro de actividad.", "warning")
        if config["profile"] == "worksheet" and config["advanced_grading"]:
            incident("ADVANCED_GRADING_UNSUPPORTED",
                     "Moodle no permite subir notas y feedback mediante la hoja sin conexión con "
                     "rúbrica o guía de evaluación avanzada activada. Conserva el análisis y acuerda "
                     "el procedimiento con el docente; no se cambia a libro de calificaciones.")
        header, rows, formatting = _read_csv(input_file, config.get("delimiter"))
        positions = {name: index for index, name in enumerate(header)}
        columns = [config[name] for name in ("identifier_column", "grade_column", "feedback_column",
                                             "activity_column", "attempt_column") if name in config]
        if any(column not in positions for column in columns):
            raise ValueError("Faltan columnas declaradas del perfil Moodle.")
        report["rows"] = len(rows)
        if not rows:
            raise ValueError("El CSV no contiene filas de participantes.")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, csv.Error) as exc:
        incident("INVALID_INPUT", str(exc))
        return finish()

    assessments, group_ids = {}, set()
    for index, entry in enumerate(evaluation["evaluations"], 1):
        try:
            members, grade = _assessment(entry, rubric, config)
            if "group_id" in entry:
                if entry["group_id"] in group_ids:
                    raise ValueError("El mismo grupo tiene varias valoraciones para esta convocatoria.")
                group_ids.add(entry["group_id"])
            for member in members:
                if member in assessments:
                    raise ValueError("Un participante tiene varias valoraciones individuales o grupales.")
            for member in members:
                assessments[member] = entry, grade
        except (ValueError, TypeError, KeyError, AttributeError, ArithmeticError) as exc:
            incident("INVALID_ASSESSMENT", str(exc), evaluation=index)

    matched, identifiers, result_rows = set(), set(), []
    for line, cells in rows:
        result = list(cells)
        result_rows.append(result)
        if any(cells[positions[config[name + "_column"]]] != config[name + "_id"]
               for name in ("activity", "attempt") if name + "_column" in config):
            continue
        identifier = cells[positions[config["identifier_column"]]]
        try:
            _identifier(identifier, "Identificador del CSV")
        except ValueError as exc:
            incident("MISSING_IDENTIFIER", str(exc), row=line)
            continue
        if identifier in identifiers:
            incident("DUPLICATE_IDENTIFIER", "Identificador repetido para la misma actividad y convocatoria.", row=line)
            continue
        identifiers.add(identifier)
        if identifier not in assessments:
            incident("NO_ASSESSMENT", "Fila conservada: no hay valoración de esta entrega.", "warning", row=line)
            continue
        entry, grade = assessments[identifier]
        matched.add(identifier)
        before = {name: cells[positions[config[name + "_column"]]] for name in ("grade", "feedback")}
        after = dict(before)
        if grade is not None:
            after = {"grade": grade["grade"], "feedback": entry["feedback"]}
            for name in ("grade", "feedback"):
                result[positions[config[name + "_column"]]] = after[name]
        else:
            incident("UNRESOLVED_SUBMISSION", "Se conservan nota y comentario para una entrega " + entry["status"] + ".",
                     "warning", identifier=identifier, row=line)
        report["audit"].append({"identifier": identifier, "row": line, "activity_id": config["activity_id"],
                                "attempt_id": config["attempt_id"], "group_id": entry.get("group_id"),
                                "status": entry["status"], "before": before, "after": after,
                                "calculation": grade, "justification": entry["justification"]})
    for identifier in assessments.keys() - matched:
        incident("UNMATCHED_ASSESSMENT", "No hay una fila Moodle inequívoca para la valoración.", identifier=identifier)

    slug = lambda value: re.sub(r"[^A-Za-z0-9_.-]", "_", value)
    target = output / f"calificaciones_{slug(config['activity_id'])}_{slug(config['attempt_id'])}.csv"
    if target.exists() or target.is_symlink():
        incident("OUTPUT_EXISTS", "Ya existe el archivo de salida; no se sobrescribe.", file=target.name)
    if target in (input_file, evaluation_file, config_file):
        incident("OUTPUT_IS_INPUT", "La salida coincide con una entrada; no se modifica.")
    if blocked():
        return finish()
    created = False
    try:
        with target.open("x", encoding="utf-8-sig", newline="") as stream:
            created = True
            writer = csv.writer(stream, **formatting)
            writer.writerow(header)
            writer.writerows(result_rows)
        report["outputs"] = [str(target)]
        report["updated"] = sum(item["status"] == "evaluated" for item in report["audit"])
    except (OSError, csv.Error) as exc:
        if created:
            target.unlink(missing_ok=True)
        incident("WRITE_FAILED", "No se exportan calificaciones: " + str(exc))
    return finish()
