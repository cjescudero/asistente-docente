"""Selección reproducible y salidas de examen desde un único modelo ordenado."""

from __future__ import annotations

import hashlib
import html
import json
import random
from pathlib import Path

from .banks import (coverage_report, load_catalog, load_selection, select_models,
                    serialize_bank)
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
    for field in ("source_bank_id", "source_question_id", "source_refs", "difficulty", "objective"):
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
    chunks = [f"$CATEGORY: examen/{model['id']}"]
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
    audience = "SOLUCIONARIO DOCENTE" if teacher else "EXAMEN · ESTUDIANTE"
    body = [f"<div class='eyebrow'>{audience}</div><h1>{html.escape(title)}</h1>",
            f"<div class='meta'>Modelo {model['id']} · {len(model['questions'])} preguntas</div>"]
    if not teacher:
        body.append("<p class='identity'>Nombre: __________________________________ Fecha: ______________</p>")
    for q in model["questions"]:
        body.append(f"<section class='question'><h2>Pregunta {q['number']:02d}</h2>")
        body.append(fragment(q["prompt"], q["format"]))
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
            if q["type"] == "multiple":
                body.append("<p><em>Seleccione todas las opciones que correspondan.</em></p>")
            body.append("<ul class='options'>")
            for option in q["options"]:
                body.append(f"<li><span class='label'>{option['label']}.</span> "
                            + fragment(option["text"], q["format"]) + "</li>")
            body.append("</ul>")
            if teacher:
                weights = "; ".join(f"{o['label']}: {number(o['weight'])}%" for o in q["options"])
                body.append(f"<p class='answer'>Crédito: {html.escape(weights)}</p>")
        body.append("</section>")
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
    for key, concept in concepts.items():
        if not isinstance(concept, dict) or not isinstance(concept.get("label", key), str):
            raise ValueError(f"Concepto no válido: {key}.")


def build_exams(bank_path: str | Path | None, output_dir: str | Path, *, title: str = "Evaluación",
                models: int = 2, questions: int = 5, seed: int = 42,
                metadata_path: str | Path | None = None, per_category: dict | None = None,
                html_only: bool = False, catalog_path: str | Path | None = None,
                selection_path: str | Path | None = None,
                project_root: str | Path | None = None, layout: str = "flat") -> dict:
    base = external_output(output_dir)
    if layout not in ("flat", "curso-v2"):
        raise ValueError("layout debe ser 'flat' o 'curso-v2'.")
    if base.exists() and any(base.iterdir()):
        raise ValueError("La carpeta de examen debe estar vacía; no se sobrescriben modelos.")
    output = base / "docente" if layout == "curso-v2" else base
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
    used = {q["id"]: 0 for q in available}
    built = []
    selections = None
    if catalog is not None:
        selections, used = select_models(bank, metadata, selection["selection"], models, rng)
        by_id = {q["id"]: q for q in bank}
    for i in range(models):
        if selections is not None:
            selected = [by_id[qid] for qid, _ in selections[i]]
        else:
            selected = []
            pools = per_category or {None: questions}
            for category, count in pools.items():
                candidates = [q for q in available if category is None or q["category"] == category]
                rng.shuffle(candidates)
                candidates.sort(key=lambda q: used[q["id"]])
                selected.extend(candidates[:count])
            for q in selected:
                used[q["id"]] += 1
            rng.shuffle(selected)
        model = {"id": model_id(i), "questions": [prepare(q, j+1, rng, metadata)
                 for j, q in enumerate(selected)], "files": {}, "pdf_status": {}}
        if selections is not None:
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
    output.mkdir(parents=True, exist_ok=True)
    if layout == "curso-v2":
        (base / "alumnado").mkdir()
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
            snapshot = f"source/{kind}.json"
            (output / snapshot).write_bytes(content)
            manifest[f"{kind}_snapshot"] = snapshot
            manifest[f"{kind}_sha256"] = hashlib.sha256(content).hexdigest()
        ids_per_model = [{q["source_id"] for q in model["questions"]} for model in built]
        manifest["selection_report"] = {
            "method": "Cuotas simultáneas con coste de reutilización y comparación de cuatro propuestas "
                      "por modelo para reducir solapamientos; sin garantía de óptimo global.",
            "question_usage": used,
            "pairwise_overlap": [
                {"models": [built[a]["id"], built[b]["id"]],
                 "shared_questions": len(ids_per_model[a] & ids_per_model[b])}
                for a in range(models) for b in range(a + 1, models)
            ],
            "coverage": {model["id"]: model["coverage"] for model in built},
        }
    for model, (student, teacher, gift) in zip(built, rendered):
        stem = f"modelo-{model['id']}"
        for role, content in [("student", student), ("teacher", teacher)]:
            role_dir = base / "alumnado" if layout == "curso-v2" and role == "student" else output
            file = role_dir / f"{stem}-{role}.html"
            file.write_text(content, encoding="utf-8")
            prefix = "../alumnado/" if role_dir != output else ""
            model["files"][f"{role}_html"] = prefix + file.name
            pdf = file.with_suffix(".pdf")
            ok, status = (False, "not_requested") if html_only else print_pdf(file, pdf)
            model["pdf_status"][role] = status
            if ok:
                model["files"][f"{role}_pdf"] = prefix + pdf.name
        gift_path = output / f"{stem}.gift"
        gift_path.write_text(gift, encoding="utf-8")
        model["files"]["gift"] = gift_path.name
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if catalog is not None:
        (output / "coverage.json").write_text(
            json.dumps(manifest["selection_report"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if layout == "curso-v2":
        record = {"schema_version": 1, "id": base.name, "type": "examen", "status": "borrador"}
        (base / "material-docente.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (base / "LEEME.md").write_text(
            "# Examen preparado\n\nEstado: **borrador**.\n\n"
            "Los documentos imprimibles están en `alumnado/`. El manifiesto, los GIFT,\n"
            "los solucionarios y las copias congeladas de los bancos están en `docente/`.\n"
            "Revisar modelos y correspondencias antes de utilizarlos. Actualizar el estado\n"
            "en este documento y en `material-docente.json`, sin mover los archivos.\n\n"
            "Después de la evaluación, se podrá preparar feedback con el manifiesto,\n"
            "el detalle por pregunta y la hoja de calificaciones de Moodle. Una nota\n"
            "global no basta para identificar dificultades conceptuales. Si ya hay\n"
            "resultados o feedback, comprobar su modelo y convocatoria antes de sugerir\n"
            "una nueva generación. La siguiente tarea requiere un encargo del docente.\n",
            encoding="utf-8")
    return manifest
