"""Selección reproducible y salidas de examen desde un único modelo ordenado."""

from __future__ import annotations

import hashlib
import html
import json
import random
from pathlib import Path

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


def build_exams(bank_path: str | Path, output_dir: str | Path, *, title: str = "Evaluación",
                models: int = 2, questions: int = 5, seed: int = 42,
                metadata_path: str | Path | None = None, per_category: dict | None = None,
                html_only: bool = False) -> dict:
    output = external_output(output_dir)
    if output.exists() and any(output.iterdir()):
        raise ValueError("La carpeta de examen debe estar vacía; no se sobrescriben modelos.")
    raw = Path(bank_path).read_bytes()
    bank = parse_gift(raw.decode("utf-8-sig"))
    metadata = (json.loads(Path(metadata_path).read_text(encoding="utf-8-sig"))
                if metadata_path else {"schema_version": 1, "questions": {}, "concepts": {}})
    validate_metadata(metadata, bank)
    if not 1 <= models <= 100 or questions < 1:
        raise ValueError("Usa entre 1 y 100 modelos y al menos una pregunta.")
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
    for i in range(models):
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
        built.append({"id": model_id(i), "questions": [prepare(q, j+1, rng, metadata)
                      for j, q in enumerate(selected)], "files": {}, "pdf_status": {}})
    # Validar todos los HTML y GIFT antes de escribir cualquier resultado.
    rendered = []
    for model in built:
        gift = obfuscated_gift(model)
        verify_obfuscated(model, gift)
        rendered.append((render_model(model, title, teacher=False),
                         render_model(model, title, teacher=True), gift))
    output.mkdir(parents=True, exist_ok=True)
    (output / "source").mkdir()
    (output / "source/bank.gift").write_bytes(raw)
    manifest = {"schema_version": 1, "title": title, "seed": seed,
                "bank_sha256": hashlib.sha256(raw).hexdigest(), "bank_snapshot": "source/bank.gift",
                "metadata": metadata, "excluded_question_ids": excluded, "models": built}
    for model, (student, teacher, gift) in zip(built, rendered):
        stem = f"modelo-{model['id']}"
        for role, content in [("student", student), ("teacher", teacher)]:
            file = output / f"{stem}-{role}.html"
            file.write_text(content, encoding="utf-8")
            model["files"][f"{role}_html"] = file.name
            pdf = file.with_suffix(".pdf")
            ok, status = (False, "not_requested") if html_only else print_pdf(file, pdf)
            model["pdf_status"][role] = status
            if ok:
                model["files"][f"{role}_pdf"] = pdf.name
        gift_path = output / f"{stem}.gift"
        gift_path.write_text(gift, encoding="utf-8")
        model["files"]["gift"] = gift_path.name
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return manifest
