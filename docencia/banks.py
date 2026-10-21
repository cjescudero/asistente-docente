"""Catálogos de bancos, procedencia verificable y selección con cuotas.

Los originales se consultan únicamente tras comprobar su selección en el curso.
El catálogo referencia materiales; no los copia ni cambia su visibilidad.
"""
from __future__ import annotations

import copy
import hashlib
import heapq
import json
import random
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path, PurePosixPath, PureWindowsPath

from .gift import escape_gift, parse_gift
from .project import find_project, load_project, source_allowed

DIFFICULTIES = {"basica", "intermedia", "avanzada"}
PRINT_TYPES = {"single", "multiple", "truefalse", "numerical"}
_BANK_ID = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
_SHA = re.compile(r"[a-f0-9]{64}\Z")


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Clave JSON duplicada: {key}.")
        value[key] = item
    return value


def _json_bytes(path: Path) -> tuple[dict, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se puede leer {path.name}: {error}") from error
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValueError(f"{path.name}: se requiere un objeto con schema_version 1.")
    return value, raw


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: se requiere texto no vacío.")
    return value


def _strings(value, label):
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{label}: se requiere una lista no vacía de textos.")
    if len(value) != len(set(value)):
        raise ValueError(f"{label}: hay valores duplicados.")
    return value


def _relative(base: Path, value, label: str) -> Path:
    """Rutas portables sin escapes ni enlaces simbólicos bajo la raíz."""
    _text(value, label)
    relative = PurePosixPath(value)
    if ("\\" in value or relative.is_absolute() or PureWindowsPath(value).drive
            or ".." in relative.parts or not relative.parts):
        raise ValueError(f"{label}: utiliza una ruta relativa dentro de su raíz.")
    current = base
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label}: no se admiten alias simbólicos: {value}.")
    if not current.resolve().is_relative_to(base):
        raise ValueError(f"{label}: la ruta sale de su raíz.")
    return current


def _material_path(root, config, material, label):
    path = _relative(root, material.get("path"), label)
    if config is not None and not source_allowed(root, config, path):
        raise ValueError(f"{label}: fuente no seleccionada o excluida: {material['path']}.")
    return path


def validate_variants(metadata: dict, bank: list[dict]):
    """Validar familias declaradas sin exigir variantes a bancos anteriores.

    Una familia reúne variantes equivalentes, no preguntas independientes sobre
    el mismo concepto. La equivalencia semántica todavía requiere revisión docente.
    """
    families = {}
    entries = metadata.get("questions", {})
    for question in bank:
        qid = question["id"]
        info = entries.get(qid, {})
        if not isinstance(info, dict):
            raise ValueError(f"Metadatos no válidos para {qid}.")
        present = {field for field in ("family_id", "variant_id") if field in info}
        if not present:
            continue
        if len(present) != 2:
            raise ValueError(f"{qid}: family_id y variant_id deben declararse juntos.")
        family = _text(info["family_id"], f"family_id de {qid}")
        variant = _text(info["variant_id"], f"variant_id de {qid}")
        concepts = _strings(info.get("concepts"), f"Conceptos de {qid}")
        objective = _text(info.get("objective"), f"Objetivo de {qid}")
        if not isinstance(info.get("difficulty"), str) or info["difficulty"] not in DIFFICULTIES:
            raise ValueError(f"Dificultad no válida en {qid}.")
        signature = (frozenset(concepts), objective, info["difficulty"])
        variants, expected = families.setdefault(family, (set(), signature))
        if variant in variants:
            raise ValueError(f"Variante duplicada {variant} en familia {family}.")
        if signature != expected:
            raise ValueError(f"Familia {family}: las variantes deben compartir conceptos, objetivo y dificultad.")
        variants.add(variant)


def family_key(qid, info):
    # Distinguish a declared family from a standalone question with the same name.
    return ("family", info["family_id"]) if "family_id" in info else ("question", qid)


def selection_diversity(built, metadata, used):
    """Informe serializable con identidad de familia inequívoca y reutilización."""
    entries = metadata.get("questions", {})
    ids_per_model = [{q["source_id"] for q in model["questions"]} for model in built]
    families_per_model = [{family_key(qid, entries.get(qid, {})) for qid in ids}
                          for ids in ids_per_model]
    usage = Counter(key for values in families_per_model for key in values)
    return {
        "method": "Cuotas simultáneas, una pregunta por familia en cada modelo y prioridad a familias "
                  "menos utilizadas, después variantes menos usadas; comparación de cuatro propuestas "
                  "para reducir solapamientos, sin garantía de óptimo global.",
        "question_usage": used,
        "family_usage": [{"kind": kind, "id": identifier, "models": count}
                         for (kind, identifier), count in sorted(usage.items())],
        "available_main_questions": len({family_key(qid, entries.get(qid, {})) for qid in used}),
        "available_question_versions": len(used),
        "pairwise_overlap": [
            {"models": [built[a]["id"], built[b]["id"]],
             "shared_questions": len(ids_per_model[a] & ids_per_model[b]),
             "shared_main_questions": len(families_per_model[a] & families_per_model[b])}
            for a in range(len(built)) for b in range(a + 1, len(built))
        ],
    }


def _check_metadata(metadata: dict, bank: list[dict], root: Path, config: dict | None):
    materials = metadata.get("materials")
    entries, concepts = metadata.get("questions"), metadata.get("concepts")
    if not isinstance(materials, dict) or not materials:
        raise ValueError("Los metadatos del catálogo requieren materials no vacío.")
    if not isinstance(entries, dict) or not isinstance(concepts, dict) or not concepts:
        raise ValueError("Los metadatos requieren questions y concepts no vacíos.")
    if set(entries) != {q["id"] for q in bank}:
        raise ValueError("Cada pregunta del banco debe tener sus metadatos, sin IDs adicionales.")
    # First validate all paths and permissions, before reading any original.
    checked_paths = {}
    for mid, material in materials.items():
        _text(mid, "Identificador de material")
        if not isinstance(material, dict):
            raise ValueError(f"Material no válido: {mid}.")
        _text(material.get("title"), f"Título del material {mid}")
        if material.get("access") not in ("estudiante", "docente"):
            raise ValueError(f"Acceso no válido en material {mid}.")
        if not isinstance(material.get("sha256"), str) or not _SHA.fullmatch(material["sha256"]):
            raise ValueError(f"Huella SHA-256 no válida en material {mid}.")
        checked_paths[mid] = _material_path(root, config, material, f"Material {mid}")
    declared_access = {}
    for mid, material in materials.items():
        path = checked_paths[mid]
        if path in declared_access and declared_access[path] != material["access"]:
            raise ValueError(f"Accesos contradictorios para el material {material['path']}.")
        declared_access[path] = material["access"]
    def check_references(entry, label):
        references = entry.get("references", [])
        if not isinstance(references, list):
            raise ValueError(f"references debe ser una lista en {label}.")
        for ref in references:
            if not isinstance(ref, dict) or ref.get("access") not in ("estudiante", "docente"):
                raise ValueError(f"Referencia no válida en {label}.")
            _text(ref.get("title"), f"Referencia de {label}")
            path = _material_path(root, config, ref, f"Referencia de {label}")
            if path not in declared_access:
                raise ValueError(f"La referencia de {label} debe apuntar a un material declarado.")
            if declared_access[path] != ref["access"]:
                raise ValueError(f"La referencia de {label} contradice el acceso del material.")

    for cid, concept in concepts.items():
        _text(cid, "Identificador de concepto")
        if not isinstance(concept, dict):
            raise ValueError(f"Concepto no válido: {cid}.")
        _text(concept.get("label"), f"Etiqueta del concepto {cid}")
        check_references(concept, f"concepto {cid}")
    for qid, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Metadatos no válidos para {qid}.")
        if any(cid not in concepts for cid in _strings(entry.get("concepts"), f"Conceptos de {qid}")):
            raise ValueError(f"Concepto no declarado en {qid}.")
        _text(entry.get("objective"), f"Objetivo de {qid}")
        _text(entry.get("guidance"), f"Orientación de repaso de {qid}")
        if not isinstance(entry.get("difficulty"), str) or entry["difficulty"] not in DIFFICULTIES:
            raise ValueError(f"Dificultad no válida en {qid}.")
        refs = entry.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError(f"source_refs es obligatorio en {qid}.")
        seen = set()
        for ref in refs:
            if (not isinstance(ref, dict) or not isinstance(ref.get("material_id"), str)
                    or ref["material_id"] not in materials):
                raise ValueError(f"Material no declarado en source_refs de {qid}.")
            if ref["material_id"] in seen:
                raise ValueError(f"Material repetido en source_refs de {qid}.")
            seen.add(ref["material_id"])
            _strings(ref.get("locators"), f"Localizadores de {qid}")
        check_references(entry, f"pregunta {qid}")
    validate_variants(metadata, bank)
    for mid, path in checked_paths.items():
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise ValueError(f"Material {mid} no accesible: {materials[mid]['path']}.") from error
        if hashlib.sha256(raw).hexdigest() != materials[mid]["sha256"]:
            raise ValueError(f"El material {mid} ha cambiado: revisar su banco antes de usarlo.")


def load_catalog(catalog_path: str | Path, *, project_root=None, bank_ids=None) -> dict:
    """Cargar bancos seleccionados con metadatos y originales congelables.

    La API pública de diagnóstico es validate_catalog. Este resultado interno
    incluye bytes para construir snapshots sin volver a leer archivos mutables.
    """
    path = Path(catalog_path).expanduser().resolve()
    catalog, catalog_raw = _json_bytes(path)
    discovered_root = find_project(path)
    root = (Path(project_root).expanduser().resolve() if project_root is not None
            else discovered_root or path.parent)
    config = load_project(root) if (root / "proyecto-docente.json").exists() else None
    path_base = catalog.get("path_base", "catalog")
    if path_base not in ("catalog", "project"):
        raise ValueError("path_base debe ser 'catalog' o 'project'.")
    if path_base == "project" and project_root is None and discovered_root is None:
        raise ValueError("path_base project requiere --project o un proyecto-docente.json cercano.")
    bank_root = root if path_base == "project" else path.parent
    rows = catalog.get("banks")
    if not isinstance(rows, list) or not rows:
        raise ValueError("El catálogo requiere una lista banks no vacía.")
    by_id, gift_paths = {}, set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not _BANK_ID.fullmatch(row["id"]):
            raise ValueError("Cada banco requiere un id estable en minúsculas, sin espacios.")
        if row["id"] in by_id:
            raise ValueError(f"Identificador de banco duplicado: {row['id']}.")
        by_id[row["id"]] = row
        for key in ("gift", "metadata"):
            _relative(bank_root, row.get(key), f"{key} de {row['id']}")
        gift_path = _relative(bank_root, row["gift"], f"GIFT de {row['id']}")
        if gift_path in gift_paths:
            raise ValueError("El catálogo registra el mismo archivo GIFT más de una vez.")
        gift_paths.add(gift_path)
    selected_ids = list(by_id) if bank_ids is None else _strings(bank_ids, "Bancos seleccionados")
    if set(selected_ids) - set(by_id):
        raise ValueError("La selección contiene bancos que no existen en el catálogo.")
    combined, originals = [], []
    merged = {"schema_version": 1, "materials": {}, "questions": {}, "concepts": {}}
    for bid in selected_ids:
        row = by_id[bid]
        gift_path = _relative(bank_root, row["gift"], f"GIFT de {bid}")
        metadata_path = _relative(bank_root, row["metadata"], f"Metadatos de {bid}")
        try:
            raw = gift_path.read_bytes()
            bank = parse_gift(raw.decode("utf-8-sig"))
        except (OSError, UnicodeError) as error:
            raise ValueError(f"No se puede leer el banco {bid}: {error}") from error
        if not bank:
            raise ValueError(f"El banco {bid} está vacío.")
        metadata, metadata_raw = _json_bytes(metadata_path)
        _check_metadata(metadata, bank, root, config)
        for section in ("materials", "concepts"):
            for key, item in metadata[section].items():
                if key in merged[section] and merged[section][key] != item:
                    raise ValueError(f"Declaraciones contradictorias de {section}/{key} entre bancos.")
                merged[section][key] = copy.deepcopy(item)
        for question in bank:
            original_id = question["id"]
            source_id = f"{bid}::{original_id}"
            combined.append({**question, "id": source_id})
            info = copy.deepcopy(metadata["questions"][original_id])
            if "family_id" in info:
                info["source_family_id"] = info["family_id"]
                info["family_id"] = f"{bid}::{info['family_id']}"
            merged["questions"][source_id] = {
                **info, "source_bank_id": bid, "source_question_id": original_id,
            }
        originals.append({"id": bid, "gift": row["gift"], "metadata": row["metadata"],
                          "gift_bytes": raw, "metadata_bytes": metadata_raw,
                          "questions": len(bank)})
    # One physical source cannot be reclassified by another bank.
    access_by_path = {}
    for material in merged["materials"].values():
        key = _relative(root, material["path"], "Material")
        if key in access_by_path and access_by_path[key] != material["access"]:
            raise ValueError(f"Accesos contradictorios entre bancos: {material['path']}.")
        access_by_path[key] = material["access"]
    return {"bank": combined, "metadata": merged, "banks": originals,
            "catalog": catalog, "catalog_bytes": catalog_raw}


def validate_catalog(catalog_path: str | Path, *, project_root=None) -> dict:
    """Validar catálogo, metadatos, permisos y huellas; no escribir archivos."""
    loaded = load_catalog(catalog_path, project_root=project_root)
    return {"status": "ok", "schema_version": 1,
            "banks": [{"id": b["id"], "questions": b["questions"]} for b in loaded["banks"]],
            "questions": len(loaded["bank"]),
            "main_questions": len({family_key(q["id"], loaded["metadata"]["questions"][q["id"]])
                                   for q in loaded["bank"]}),
            "materials": len(loaded["metadata"]["materials"]),
            "concepts": len(loaded["metadata"]["concepts"]),
            "diagnostics": []}


def load_selection(selection_path: str | Path, questions: int) -> dict:
    selection, raw = _json_bytes(Path(selection_path).expanduser().resolve())
    _strings(selection.get("banks"), "Bancos seleccionados")
    quotas = selection.get("quotas")
    if not isinstance(quotas, list) or not quotas:
        raise ValueError("La selección requiere quotas no vacías.")
    labels = set()
    for quota in quotas:
        if not isinstance(quota, dict):
            raise ValueError("Cada cuota debe ser un objeto.")
        label = _text(quota.get("label"), "Etiqueta de cuota")
        if label in labels:
            raise ValueError(f"Etiqueta de cuota duplicada: {label}.")
        labels.add(label)
        if type(quota.get("count")) is not int or quota["count"] < 1:
            raise ValueError(f"La cuota {label} requiere count entero positivo.")
        if set(quota) - {"label", "count", "material_ids", "concepts", "difficulty", "types"}:
            raise ValueError(f"Filtro desconocido en la cuota {label}.")
        for field in ("material_ids", "concepts", "types"):
            if field in quota:
                _strings(quota[field], f"{field} de {label}")
        if "difficulty" in quota and (not isinstance(quota["difficulty"], str) or quota["difficulty"] not in DIFFICULTIES):
            raise ValueError(f"Dificultad no válida en cuota {label}.")
        if "types" in quota and set(quota["types"]) - PRINT_TYPES:
            raise ValueError(f"Tipos no imprimibles o desconocidos en cuota {label}.")
    if sum(quota["count"] for quota in quotas) != questions:
        raise ValueError("La suma de cuotas debe coincidir con --questions.")
    return {"selection": selection, "selection_bytes": raw}


def _eligible(question, info, quota):
    return (question["type"] in PRINT_TYPES
            and ("types" not in quota or question["type"] in quota["types"])
            and ("difficulty" not in quota or info["difficulty"] == quota["difficulty"])
            and ("concepts" not in quota or bool(set(info["concepts"]) & set(quota["concepts"])))
            and ("material_ids" not in quota or bool(
                {ref["material_id"] for ref in info["source_refs"]} & set(quota["material_ids"]))))


def _matching(slots, candidates, usage, rng, families=None, family_usage=None):
    """Minimum-cost complete matching; reverse edges handle overlapping quotas."""
    ids = sorted({qid for values in candidates for qid in values})
    n_slots = len(slots)
    families = families or {qid: ("question", qid) for qid in ids}
    family_usage = family_usage or Counter()
    family_ids = sorted({families[qid] for qid in ids})
    source, sink = 0, n_slots + len(ids) + len(family_ids) + 1
    graph = [[] for _ in range(sink + 1)]
    positions = {qid: n_slots + 1 + i for i, qid in enumerate(ids)}
    family_positions = {key: n_slots + len(ids) + 1 + i for i, key in enumerate(family_ids)}

    def edge(start, end, capacity, cost):
        forward = [end, len(graph[end]), capacity, cost]
        reverse = [start, len(graph[start]), 0, -cost]
        graph[start].append(forward)
        graph[end].append(reverse)

    ranks = ids[:]
    rng.shuffle(ranks)
    tie = {qid: index for index, qid in enumerate(ranks)}
    # Any unit of global reuse outweighs the sum of all random tie-breaks.
    priority = (len(ids) + 1) * (n_slots + 1)
    family_priority = (max(usage.values(), default=0) + 1) * (n_slots + 1) * priority
    for index, quota_index in enumerate(slots):
        node = index + 1
        edge(source, node, 1, 0)
        for qid in candidates[quota_index]:
            cost = (family_usage[families[qid]] * family_priority
                    + usage[qid] * priority + tie[qid])
            edge(node, positions[qid], 1, cost)
    for qid, node in positions.items():
        edge(node, family_positions[families[qid]], 1, 0)
    for node in family_positions.values():
        edge(node, sink, 1, 0)
    potential = [0] * len(graph)
    for _ in slots:
        distance = [float("inf")] * len(graph)
        distance[source] = 0
        previous = [None] * len(graph)
        queue = [(0, source)]
        while queue:
            cost, node = heapq.heappop(queue)
            if cost != distance[node]:
                continue
            for index, (target, _, capacity, value) in enumerate(graph[node]):
                if not capacity:
                    continue
                new = cost + value + potential[node] - potential[target]
                if new < distance[target]:
                    distance[target] = new
                    previous[target] = (node, index)
                    heapq.heappush(queue, (new, target))
        if previous[sink] is None:
            raise ValueError("Fondo insuficiente para cumplir simultáneamente las cuotas sin repetir preguntas principales/familias; "
                             "revisar su solapamiento o ampliar los bancos.")
        for node, cost in enumerate(distance):
            if cost < float("inf"):
                potential[node] += cost
        node = sink
        while node != source:
            start, index = previous[node]
            target, reverse, _, _ = graph[start][index]
            graph[start][index][2] -= 1
            graph[target][reverse][2] += 1
            node = start
    question_for_node = {node: qid for qid, node in positions.items()}
    return [(question_for_node[target], slots[index])
            for index in range(n_slots)
            for target, _, capacity, _ in graph[index + 1]
            if target in question_for_node and capacity == 0]


def select_models(bank, metadata, selection, models, rng):
    quotas = selection["quotas"]
    for quota in quotas:
        for field, section in (("concepts", "concepts"), ("material_ids", "materials")):
            if set(quota.get(field, [])) - set(metadata[section]):
                raise ValueError(f"La cuota {quota['label']} referencia {field} no declarados.")
    candidates = [[q["id"] for q in bank if _eligible(q, metadata["questions"][q["id"]], quota)]
                  for quota in quotas]
    for quota, pool in zip(quotas, candidates):
        if len(pool) < quota["count"]:
            raise ValueError(f"Fondo insuficiente en {quota['label']}: {len(pool)} preguntas compatibles "
                             f"para {quota['count']} solicitadas.")
    slots = [index for index, quota in enumerate(quotas) for _ in range(quota["count"])]
    return _choose_models(bank, metadata, candidates, slots, models, rng)


def select_flat_models(bank, metadata, questions, per_category, models, rng):
    """Mantener banco único y cuotas por categoría sin repetir familias."""
    pools = per_category or {None: questions}
    candidates, slots = [], []
    for index, (category, count) in enumerate(pools.items()):
        candidates.append([q["id"] for q in bank if q["type"] in PRINT_TYPES
                           and (category is None or q["category"] == category)])
        slots.extend([index] * count)
    return _choose_models(bank, metadata, candidates, slots, models, rng)


def _choose_models(bank, metadata, candidates, slots, models, rng):
    entries = metadata.get("questions", {})
    used = {q["id"]: 0 for q in bank if q["type"] in PRINT_TYPES}
    families = {qid: family_key(qid, entries.get(qid, {})) for qid in used}
    family_usage = Counter()
    previous, previous_families, built = [], [], []
    for _ in range(models):
        proposals = [_matching(slots, candidates, used, rng, families, family_usage) for _ in range(4)]

        def preference(proposal):
            chosen = {qid for qid, _ in proposal}
            chosen_families = {families[qid] for qid in chosen}
            overlaps = [len(chosen & seen) for seen in previous]
            family_overlaps = [len(chosen_families & seen) for seen in previous_families]
            return (sum(family_usage[key] for key in chosen_families),
                    sum(used[qid] for qid in chosen), max(family_overlaps, default=0),
                    sum(value * value for value in family_overlaps),
                    max(overlaps, default=0), sum(value * value for value in overlaps))

        chosen = min(proposals, key=preference)
        for qid, _ in chosen:
            used[qid] += 1
            family_usage[families[qid]] += 1
        previous.append({qid for qid, _ in chosen})
        previous_families.append({families[qid] for qid, _ in chosen})
        rng.shuffle(chosen)
        built.append(chosen)
    return built, used


def coverage_report(selected, metadata, quotas):
    infos = [metadata["questions"][qid] for qid, _ in selected]
    return {"quotas": dict(Counter(quotas[index]["label"] for _, index in selected)),
            "difficulty": dict(Counter(info["difficulty"] for info in infos)),
            "concepts": dict(Counter(cid for info in infos for cid in info["concepts"])),
            "materials": dict(Counter(ref["material_id"] for info in infos for ref in info["source_refs"]))}


def serialize_bank(bank: list[dict]) -> bytes:
    """Serializar el subconjunto GIFT completo, comprobando su ida y vuelta."""
    # GIFT cannot reset its category to empty: uncategorized questions go first.
    ordered = sorted(bank, key=lambda q: bool(q["category"]))
    chunks = []
    for question in ordered:
        if question["category"]:
            chunks.append("$CATEGORY: " + escape_gift(question["category"]))
        kind = question["type"]
        if kind in {"single", "multiple"}:
            answers = []
            for option in question["options"]:
                weight = option["weight"]
                prefix = "=" if kind == "single" and weight == 100 else "~"
                if prefix == "~" and weight:
                    prefix += f"%{format(Decimal(str(weight)), 'f')}%"
                answer = prefix + escape_gift(option["text"])
                if option.get("feedback"):
                    answer += "#" + escape_gift(option["feedback"])
                answers.append(answer)
            body = "\n".join(answers)
        elif kind == "truefalse":
            body = "TRUE" if question["true_answer"] else "FALSE"
            if question.get("options"):
                feedback = {option["weight"] == 100: option["feedback"] for option in question["options"]}
                body += "#" + escape_gift(feedback[False]) + "#" + escape_gift(feedback[True])
        elif kind == "numerical":
            answers = []
            for answer in question["numerical"]:
                value = (f"{answer['min']}..{answer['max']}" if "min" in answer
                         else f"{answer['value']}:{answer.get('tolerance', 0)}")
                value = f"=%{format(Decimal(str(answer['weight'])), 'f')}%{value}"
                if answer.get("feedback"):
                    value += "#" + escape_gift(answer["feedback"])
                answers.append(value)
            body = "#\n" + "\n".join(answers)
        elif kind == "matching":
            body = "\n".join("=" + escape_gift(pair["left"]) + "->" + escape_gift(pair["right"])
                             for pair in question["matches"])
        else:
            raise ValueError(f"Tipo GIFT no serializable: {kind}.")
        if "feedback" in question:
            body += "\n####" + escape_gift(question["feedback"])
        chunks.append(f"::{escape_gift(question['id'])}::[{question['format']}]"
                      f"{escape_gift(question['prompt'])} {{\n{body}\n}}")
    text = "\n\n".join(chunks) + "\n"
    if parse_gift(text) != ordered:
        raise ValueError("La serialización del banco combinado ha alterado sus preguntas.")
    return text.encode("utf-8")
