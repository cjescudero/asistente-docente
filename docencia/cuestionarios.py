"""Selección reproducible y salidas de cuestionario desde un único modelo ordenado."""

from __future__ import annotations

import hashlib
import html
import json
import random
from pathlib import Path

from .banks import (coverage_report, load_catalog, load_selection, select_models,
                    select_flat_models, selection_diversity, serialize_bank, validate_variants)
from .gift import parse_gift
from .render import document, external_output, fragment, print_pdf

SUPPORTED = {"single", "multiple", "truefalse", "numerical"}


def number(value: float) -> str:
    """Representación decimal que conserva el valor binario al releerlo."""
    return str(float(value))


def model_id(index: int) -> str:
    result = ""
    while index >= 0:
        result = chr(65 + index % 26) + result
        index = index // 26 - 1
    return result


def prepare(question: dict, number: int, rng: random.Random, metadata: dict) -> dict:
    info = metadata.get("questions", {}).get(question["id"], {})
    result = {"number": number, "source_id": question["id"],
              "source_category": question["category"], "concepts": info.get("concepts", []),
              "type": question["type"], "prompt": question["prompt"],
              "format": question["format"]}
    for field in ("source_bank_id", "source_question_id", "source_refs", "difficulty", "objective",
                  "family_id", "source_family_id", "variant_id"):
        if field in info:
            result[field] = info[field]
    if question["type"] == "numerical":
        result["numerical"] = question["numerical"]
        return result
    options = question.get("options", [])
    if question["type"] == "truefalse" and not options:
        options = [{"text": "Verdadero", "weight": 100 if question["true_answer"] else 0},
                   {"text": "Falso", "weight": 0 if question["true_answer"] else 100}]
    order = list(range(len(options)))
    rng.shuffle(order)
    result["options"] = [{"label": model_id(i), "text": options[j]["text"],
                          "weight": options[j]["weight"], "source_index": j}
                         for i, j in enumerate(order)]
    return result


def numeric_body(values: list[dict]) -> str:
    lines = []
    for item in values:
        value = (f"{number(item['min'])}..{number(item['max'])}" if "min" in item
                 else f"{number(item['value'])}:{number(item.get('tolerance', 0))}")
        weight = item.get("weight", 100)
        lines.append(f"=%{number(weight)}%{value}")
    return "#\n" + "\n".join(lines)


def obfuscated_gift(model: dict) -> str:
    chunks = [f"$CATEGORY: {model.get('moodle_category', 'cuestionario/' + model['id'])}"]
    for q in model["questions"]:
        if q["type"] == "numerical":
            body = numeric_body(q["numerical"])
        else:
            lines = []
            for option in q["options"]:  # El orden visible es la autoridad.
                weight = option["weight"]
                if q["type"] != "multiple" and weight == 100:
                    prefix = "="
                else:
                    prefix = "~" if weight == 0 else f"~%{number(weight)}%"
                lines.append(f"{prefix}Respuesta {option['label']}")
            body = "\n" + "\n".join(lines)
        chunks.append(f"::{model['id']}-P{q['number']:03d}::[plain]Pregunta {q['number']:02d} {{{body}\n}}")
    return "\n\n".join(chunks) + "\n"


def verify_obfuscated(model: dict, text: str):
    parsed = parse_gift(text)
    if len(parsed) != len(model["questions"]):
        raise ValueError("Error interno: recuento GIFT inconsistente.")
    for source, exported in zip(model["questions"], parsed):
        if "moodle_category" in model and exported["category"] != model["moodle_category"]:
            raise ValueError("La categoría Moodle no coincide con el manifiesto.")
        if exported["prompt"] != f"Pregunta {source['number']:02d}":
            raise ValueError("La numeración GIFT no coincide con el modelo.")
        if source["type"] == "numerical":
            actual = [{k:v for k,v in x.items() if k != "feedback"} for x in exported["numerical"]]
            expected = [{k:v for k,v in x.items() if k != "feedback"} for x in source["numerical"]]
            if actual != expected:
                raise ValueError("Los criterios numéricos cambiaron al exportar GIFT.")
        else:
            expected_type = "single" if source["type"] == "truefalse" else source["type"]
            expected = [(f"Respuesta {o['label']}", o["weight"]) for o in source["options"]]
            actual = [(o["text"], o["weight"]) for o in exported["options"]]
            if exported["type"] != expected_type or actual != expected:
                raise ValueError("El tipo, el orden o los pesos cambiaron al exportar GIFT.")


def render_model(model: dict, title: str, *, teacher: bool) -> str:
    audience = "SOLUCIONARIO DOCENTE" if teacher else "CUESTIONARIO"
    body = ["<div class='questionnaire'>",
            f"<header class='questionnaire-header'><h1>{html.escape(title)}</h1>"
            f"<div class='model-id'>{html.escape(model.get('name', 'Modelo ' + str(model['id'])))}</div></header>"]
    if teacher:
        body.append(f"<p class='eyebrow'>{audience}</p>")
    else:
        body.append("<div class='identity-grid'><div>APELLIDOS Y NOMBRE<span></span></div>"
                    "<div>EMAIL<span></span></div></div>")
        body.append(f"<aside class='instructions'>{len(model['questions'])} preguntas. "
                    "Marque sus respuestas en papel y traslade la misma opción o valor a Moodle. "
                    "Círculo: una respuesta; cuadrado: varias respuestas. "
                    "Las respuestas en blanco valen 0. Los créditos corresponden a una pregunta de 1 punto.</aside>")
    for q in model["questions"]:
        kind = {"single": "UNA RESPUESTA", "multiple": "VARIAS RESPUESTAS", "truefalse": "VERDADERO/FALSO", "numerical": "NUMÉRICA"}[q["type"]]
        body.append(f"<section class='question'><div class='question-heading'><h2>Pregunta {q['number']:02d}</h2><span>{kind}</span></div>")
        body.append(fragment(q["prompt"], q["format"]))
        if not teacher:
            if q["type"] == "numerical":
                credits = sorted({a.get("weight", 100) / 100 for a in q["numerical"]})
                instruction = "Escriba un valor numérico. Crédito aceptado: " + ", ".join(number(x) for x in credits) + "; fuera de los valores admitidos: 0."
            else:
                positive = sorted({o["weight"] / 100 for o in q["options"] if o["weight"] > 0})
                other = sorted({o["weight"] / 100 for o in q["options"] if o["weight"] <= 0})
                instruction = ("Marque las opciones que correspondan. Se suman los créditos de las opciones marcadas. "
                               if q["type"] == "multiple" else "Marque una sola opción. ")
                instruction += "Crédito por acierto: " + ", ".join(number(x) for x in positive)
                instruction += "; por error: " + ", ".join(number(x) for x in other) + "."

            body.append("<p class='scoring'>" + html.escape(instruction) + "</p>")
        if q["type"] == "numerical":
            body.append("<p class='numeric'>Respuesta: __________________________</p>")
            if teacher:
                answers = []
                for answer in q["numerical"]:
                    value = (f"Intervalo: {number(answer['min'])} a {number(answer['max'])}" if "min" in answer
                             else f"Valor: {number(answer['value'])}; tolerancia: ±{number(answer.get('tolerance',0))}")
                    answers.append(f"{value}; crédito: {number(answer.get('weight',100))}%")
                body.append(f"<p class='answer'>{'<br>'.join(html.escape(x) for x in answers)}</p>")
        else:
            shape = "square" if q["type"] == "multiple" else "circle"
            body.append(f"<ul class='options {shape}'>")
            for option in q["options"]:
                body.append(f"<li><span class='label'>{option['label']}</span> "
                            + fragment(option["text"], q["format"]) + "</li>")
            body.append("</ul>")
            if teacher:
                weights = "; ".join(f"{o['label']}: {number(o['weight'])}%" for o in q["options"])
                body.append(f"<p class='answer'>Crédito: {html.escape(weights)}</p>")
        body.append("</section>")
    body.append("</div>")
    content = "".join(body)
    return document(title, content, math="\\(" in content or "\\[" in content)


def validate_metadata(metadata: dict, bank: list[dict]):
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        raise ValueError("Metadatos: se requiere schema_version 1.")
    entries = metadata.get("questions", {})
    concepts = metadata.get("concepts", {})
    if not isinstance(entries, dict) or not isinstance(concepts, dict):
        raise ValueError("Metadatos questions y concepts deben ser objetos.")
    ids = {q["id"] for q in bank}
    if set(entries) - ids:
        raise ValueError("Los metadatos contienen identificadores que no existen en el banco.")
    for qid, entry in entries.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("concepts", []), list):
            raise ValueError(f"Metadatos no válidos para {qid}.")
        if any(not isinstance(x, str) or x not in concepts for x in entry.get("concepts", [])):
            raise ValueError(f"Concepto no declarado en {qid}.")
    validate_variants(metadata, bank)
    for key, concept in concepts.items():
        if not isinstance(concept, dict) or not isinstance(concept.get("label", key), str):
            raise ValueError(f"Concepto no válido: {key}.")


def build_cuestionarios(bank_path: str | Path | None, output_dir: str | Path, *, title: str = "Cuestionario",
                models: int = 4, questions: int = 5, seed: int = 42,
                metadata_path: str | Path | None = None, per_category: dict | None = None,
                html_only: bool = False, catalog_path: str | Path | None = None,
                selection_path: str | Path | None = None,
                project_root: str | Path | None = None, layout: str = "flat") -> dict:
    base = external_output(output_dir)
    if layout not in ("flat", "curso-v3"):
        raise ValueError("layout debe ser 'flat' o 'curso-v3'.")
    selection_target = base / "_datos_internos/seleccion.json"
    if layout == "curso-v3" and catalog_path is not None:
        if selection_path is None or Path(selection_path).resolve() != selection_target.resolve():
            raise ValueError("En curso-v3 guarda --selection en <cuestionario>/_datos_internos/seleccion.json.")
        if selection_target.is_symlink() or not selection_target.is_file():
            raise ValueError("La selección previa debe ser un archivo regular.")
    if base.exists():
        if not base.is_dir() or base.is_symlink():
            raise ValueError("El destino del cuestionario debe ser una carpeta regular.")
        allowed = (layout == "curso-v3" and catalog_path is not None
                   and {p.name for p in base.iterdir()} == {"_datos_internos"}
                   and selection_target.parent.is_dir() and not selection_target.parent.is_symlink()
                   and {p.name for p in selection_target.parent.iterdir()} == {"seleccion.json"})
        if any(base.iterdir()) and not allowed:
            raise ValueError("La carpeta de cuestionario debe estar vacía salvo la selección previa; no se sobrescriben modelos.")
    output = base / "_datos_internos" if layout == "curso-v3" else base
    teacher_dir = base / "docente" if layout == "curso-v3" else output
    if (type(models) is not int or type(questions) is not int
            or not 1 <= models <= 100 or questions < 1):
        raise ValueError("Usa entre 1 y 100 modelos y al menos una pregunta.")
    catalog = selection = None
    if catalog_path is not None:
        if bank_path is not None or metadata_path is not None or per_category is not None:
            raise ValueError("El catálogo no se combina con banco único, metadatos externos o cuotas por categoría.")
        if selection_path is None:
            raise ValueError("El catálogo requiere un archivo de selección explícita.")
        selection = load_selection(selection_path, questions)
        catalog = load_catalog(catalog_path, project_root=project_root,
                               bank_ids=selection["selection"]["banks"])
        bank, metadata = catalog["bank"], catalog["metadata"]
        raw = serialize_bank(bank)
    else:
        if bank_path is None or selection_path is not None:
            raise ValueError("Indica un banco GIFT o un catálogo con su selección.")
        raw = Path(bank_path).read_bytes()
        bank = parse_gift(raw.decode("utf-8-sig"))
        metadata = (json.loads(Path(metadata_path).read_text(encoding="utf-8-sig"))
                    if metadata_path else {"schema_version": 1, "questions": {}, "concepts": {}})
        validate_metadata(metadata, bank)
    available = [q for q in bank if q["type"] in SUPPORTED]
    excluded = [q["id"] for q in bank if q["type"] not in SUPPORTED]
    if len(available) < questions:
        raise ValueError(f"Banco insuficiente: {len(available)} preguntas compatibles para {questions} solicitadas.")
    if per_category is not None:
        if (not isinstance(per_category, dict) or
            any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in per_category.values()) or
            sum(per_category.values()) != questions):
            raise ValueError("Las cuotas por categoría deben ser enteros no negativos y sumar --questions.")
        for category, count in per_category.items():
            if sum(q["category"] == category for q in available) < count:
                raise ValueError(f"Banco insuficiente en categoría {category}.")
    rng = random.Random(seed)
    built = []
    if catalog is not None:
        selections, used = select_models(bank, metadata, selection["selection"], models, rng)
    else:
        selections, used = select_flat_models(bank, metadata, questions, per_category, models, rng)
    if not title.strip() or any(c in title for c in "\r\n/{}\\"):
        raise ValueError("El título debe ser un nombre de cuestionario sin saltos de línea ni /, llaves o barras inversas para su categoría Moodle.")
    by_id = {q["id"]: q for q in bank}
    for i in range(models):
        selected = [by_id[qid] for qid, _ in selections[i]]
        model = {"id": model_id(i), "questions": [prepare(q, j+1, rng, metadata)
                 for j, q in enumerate(selected)], "files": {}, "pdf_status": {}}
        model["name"] = f"Modelo {i + 1:02d}"
        model["moodle_category"] = f"$course$/top/RespuestasCuestionariosOffline/{title}/{model['name']}"
        if catalog is not None:
            for prepared, (_, quota) in zip(model["questions"], selections[i]):
                prepared["quota_label"] = selection["selection"]["quotas"][quota]["label"]
            model["coverage"] = coverage_report(selections[i], metadata, selection["selection"]["quotas"])
        built.append(model)
    # Validar todos los HTML y GIFT antes de escribir cualquier resultado.
    rendered = []
    for model in built:
        gift = obfuscated_gift(model)
        verify_obfuscated(model, gift)
        rendered.append((render_model(model, title, teacher=False),
                         render_model(model, title, teacher=True), gift))
    if layout == "curso-v3" and catalog is not None and selection_target.read_bytes() != selection["selection_bytes"]:
        raise ValueError("La selección cambió durante la preparación del cuestionario.")
    output.mkdir(parents=True, exist_ok=True)
    if layout == "curso-v3":
        (base / "alumnado").mkdir()
    if layout == "curso-v3":
        teacher_dir.mkdir()
    (output / "source").mkdir()
    (output / "source/bank.gift").write_bytes(raw)
    manifest = {"schema_version": 1, "title": title, "seed": seed,
                "bank_sha256": hashlib.sha256(raw).hexdigest(), "bank_snapshot": "source/bank.gift",
                "metadata": metadata, "excluded_question_ids": excluded, "models": built}
    if catalog is not None:
        (output / "source/banks").mkdir()
        manifest["source_banks"] = []
        for original in catalog["banks"]:
            entry = {"id": original["id"], "questions": original["questions"]}
            for field, suffix in (("gift", ".gift"), ("metadata", ".metadata.json")):
                snapshot = f"source/banks/{original['id']}{suffix}"
                content = original[f"{field}_bytes"]
                (output / snapshot).write_bytes(content)
                entry[f"{field}_snapshot"] = snapshot
                entry[f"{field}_sha256"] = hashlib.sha256(content).hexdigest()
            manifest["source_banks"].append(entry)
        for kind, content in (("catalog", catalog["catalog_bytes"]),
                              ("selection", selection["selection_bytes"])):
            if layout == "curso-v3" and kind == "selection":
                manifest[f"{kind}_snapshot"] = "seleccion.json"
                manifest[f"{kind}_sha256"] = hashlib.sha256(content).hexdigest()
                continue
            snapshot = f"source/{kind}.json"
            (output / snapshot).write_bytes(content)
            manifest[f"{kind}_snapshot"] = snapshot
            manifest[f"{kind}_sha256"] = hashlib.sha256(content).hexdigest()
    manifest["selection_report"] = selection_diversity(built, metadata, used)
    if catalog is not None:
        manifest["selection_report"]["coverage"] = {model["id"]: model["coverage"] for model in built}
    for model, (student, teacher, gift) in zip(built, rendered):
        stem = f"modelo-{model['id']}"
        for role, content in [("student", student), ("teacher", teacher)]:
            role_dir = (base / "alumnado" if layout == "curso-v3" and role == "student"
                        else teacher_dir if layout == "curso-v3" and role == "teacher" else output)
            file = role_dir / f"{stem}-{role}.html"
            file.write_text(content, encoding="utf-8")
            prefix = ("../alumnado/" if layout == "curso-v3" and role == "student" else
                      "../docente/" if layout == "curso-v3" and role == "teacher" else
                      "../alumnado/" if role_dir != output else "")
            model["files"][f"{role}_html"] = prefix + file.name
            pdf = file.with_suffix(".pdf")
            ok, status = (False, "not_requested") if html_only else print_pdf(file, pdf)
            model["pdf_status"][role] = status
            if ok:
                model["files"][f"{role}_pdf"] = prefix + pdf.name
        gift_path = teacher_dir / f"{stem}.gift"
        gift_path.write_text(gift, encoding="utf-8")
        model["files"]["gift"] = ("../docente/" if layout == "curso-v3" else "") + gift_path.name
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if catalog is not None:
        (output / "coverage.json").write_text(
            json.dumps(manifest["selection_report"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if layout == "curso-v3":
        record = {"schema_version": 1, "id": base.name, "type": "cuestionario", "status": "borrador"}
        record_path = output / "material-docente.json"
        record_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        links = []
        if layout == "curso-v3":
            links.append("## Modelos y archivos\n")
            for model in built:
                files = model["files"]
                name = model["id"]
                items = [f"[Modelo {name} (HTML)](alumnado/modelo-{name}-student.html)"]
                if "student_pdf" in files:
                    items.append(f"[PDF para imprimir](alumnado/modelo-{name}-student.pdf)")
                items.append(f"[Solucionario](docente/modelo-{name}-teacher.html)")
                if "teacher_pdf" in files:
                    items.append(f"[PDF docente](docente/modelo-{name}-teacher.pdf)")
                items.append(f"[GIFT para Moodle](docente/modelo-{name}.gift)")
                links.append(f"- **{model['name']} (ID {name}):** " + " · ".join(items) + f". Categoría Moodle: `{model['moodle_category']}`")
            controls = ["[Manifiesto](_datos_internos/manifest.json)"]
            if catalog is not None:
                controls = ["[Selección](_datos_internos/seleccion.json)", *controls,
                            "[Informe de cobertura](_datos_internos/coverage.json)"]
            links.append("\n" + " · ".join(controls) + "\n")
        (base / "LEEME.md").write_text(
            "# Cuestionario preparado\n\nEstado: **borrador**.\n\n"
            "Abre los modelos imprimibles en `alumnado/` y los solucionarios y GIFT\n"
            "en `docente/`. La selección, el manifiesto y los bancos congelados\n"
            "están en `_datos_internos/`.\n"
            "Revisar modelos y correspondencias antes de utilizarlos. Actualizar el estado\n"
            "en este documento y en el registro técnico, sin mover los archivos.\n\n"
            "Después de la evaluación, se podrá preparar feedback con el manifiesto,\n"
            "el detalle por pregunta y la hoja de calificaciones de Moodle. Una nota\n"
            "global no basta para identificar dificultades conceptuales. Si ya hay\n"
            "resultados o feedback, comprobar su modelo y convocatoria antes de sugerir\n"
            "una nueva generación. La siguiente tarea requiere un encargo del docente.\n\n"
            + ("\n".join(links) + "\n" if links else ""),
            encoding="utf-8")
    return manifest
