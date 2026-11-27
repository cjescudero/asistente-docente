"""Catálogos de bancos, procedencia verificable y selección con cuotas.

Los originales se consultan únicamente tras comprobar su selección en el curso.
El catálogo referencia materiales; no los copia ni cambia su visibilidad.
"""
from __future__ import annotations

import copy
import hashlib
import heapq
import json
import os
import random
import re
import stat
from collections import Counter
from decimal import Decimal
from pathlib import Path, PurePosixPath, PureWindowsPath
from uuid import UUID

from .language_context import with_diagnostics
from .quiz_language import diagnostic
from .gift import escape_gift, parse_gift
from .project import INTERNAL_MATERIAL_DIR, _safe_path, _within_relative, find_project, load_project, source_allowed
from .spaces import corpus_policy, under, reserved, key as path_key

DIFFICULTIES = {"basica", "intermedia", "avanzada"}
PRINT_TYPES = {"single", "multiple", "truefalse", "numerical"}
_BANK_ID = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
_SHA = re.compile(r"[a-f0-9]{64}\Z")


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(diagnostic("Clave JSON duplicada: {key}.", key=key))
        value[key] = item
    return value


def _json_bytes(path: Path) -> tuple[dict, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(diagnostic("No se puede leer {name}: {error}", name=path.name, error=error)) from error
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValueError(diagnostic("{name}: se requiere un objeto con schema_version 1.", name=path.name))
    return value, raw


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(diagnostic("{label}: se requiere texto no vacío.", label=label))
    return value


def _strings(value, label):
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(diagnostic("{label}: se requiere una lista no vacía de textos.", label=label))
    if len(value) != len(set(value)):
        raise ValueError(diagnostic("{label}: hay valores duplicados.", label=label))
    return value


def _relative(base: Path, value, label: str) -> Path:
    """Rutas portables sin escapes ni enlaces simbólicos bajo la raíz."""
    _text(value, label)
    relative = PurePosixPath(value)
    if ("\\" in value or relative.is_absolute() or PureWindowsPath(value).drive
            or ".." in relative.parts or not relative.parts):
        raise ValueError(diagnostic("{label}: utiliza una ruta relativa dentro de su raíz.", label=label))
    current = base
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(diagnostic("{label}: no se admiten alias simbólicos: {value}.", label=label, value=value))
    if not current.resolve().is_relative_to(base):
        raise ValueError(diagnostic("{label}: la ruta sale de su raíz.", label=label))
    return current


def _uuid(value):
    try:
        return str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


class _BankInputs:
    """Comprobar por separado los archivos del banco, sus fuentes y sus destinatarios."""

    def __init__(self, root, config, direct):
        self.root = root
        self.config = config
        self.v4 = config is not None and config.get("structure") == "curso-v4"
        self.records = {}
        self.paths = {}
        self.disputed = set()
        self.direct = set()
        if self.v4:
            self.config = {**config, "sources": corpus_policy(root, config)}
            from .catalog import read_catalog
            ledger = read_catalog(root)
            self.records = ledger["materials"]
            self.paths = {r["path"]: r for r in self.records.values() if r.get("path")}
            self.disputed = set(ledger.get("identity_questions", {}))
        for item in direct or []:
            if not self.v4:
                raise ValueError(diagnostic("La selección directa de actividades generadas requiere un curso-v4."))
            row = self.records.get(item, {})
            relative = row.get("path") if _uuid(item) else item
            path = _relative(root, relative, diagnostic("Material elegido"))
            if not self._generated(relative) or not path.is_file() or reserved(relative):
                raise ValueError(diagnostic("Elegir el archivo concreto de la actividad generada: {item}.", item=item))
            self._check_boundary(path, internal=False)
            self.direct.add(path)

    def _generated(self, relative):
        return any(_within_relative(relative, base) for base in self.config["spaces"]["generated"])

    def _check_boundary(self, path, *, internal):
        if not path.is_relative_to(self.root):
            raise ValueError(diagnostic("El archivo queda fuera del curso."))
        relative = path.relative_to(self.root).as_posix()
        _safe_path(self.root, relative)
        blocked = self.config["spaces"]["submissions"] + self.config["sources"]["exclude"]
        if self.config["map"]:
            blocked = [*blocked, self.config["map"]]
        if any(under(relative, base) for base in blocked):
            raise ValueError(diagnostic("Ruta excluida del proceso de bancos: {relative}.", relative=relative))
        from .catalog import unreadable_entry
        if path.exists():
            st = path.stat()
            if unreadable_entry(st) or not stat.S_ISREG(st.st_mode):
                raise ValueError(diagnostic("Entrada no disponible como archivo regular local: {relative}.", relative=relative))
        parts = PurePosixPath(relative).parts
        if any((reserved(part) or part.startswith(".")) and
               not (internal and path_key(part) == path_key(INTERNAL_MATERIAL_DIR)) for part in parts):
            raise ValueError(diagnostic("Ruta operativa excluida del proceso de bancos: {relative}.", relative=relative))
        return relative

    def check_bank_file(self, path, role):
        if not self.v4:
            return
        relative = self._check_boundary(path, internal=role in ("metadata", "catalog"))
        if self._generated(relative):
            return
        sources = self.config["sources"]
        if not sources["selected"] or not any(_within_relative(relative, base) for base in sources["include"]):
            raise ValueError(diagnostic("Archivo de banco fuera de la selección del curso: {relative}.", relative=relative))
        # Un catálogo o unos metadatos pueden residir en el control de un banco.
        anchor = path
        while INTERNAL_MATERIAL_DIR in anchor.relative_to(self.root).parts:
            anchor = anchor.parent
        if not source_allowed(self.root, self.config, anchor):
            raise ValueError(diagnostic("Archivo de banco de una fuente no seleccionada o excluida: {relative}.", relative=relative))

    def check_digest(self, mid, path, material):
        try:
            st = path.stat()
            row = self.paths.get(path.relative_to(self.root).as_posix())
            if (row and row["sha256"] and row.get("physical_id") == {"dev": st.st_dev, "ino": st.st_ino}
                    and row["size"] == st.st_size and row["mtime_ns"] == st.st_mtime_ns
                    and row.get("ctime_ns") == st.st_ctime_ns):
                digest = row["sha256"]
            else:
                if not stat.S_ISREG(st.st_mode):
                    raise ValueError(diagnostic("El material {mid} debe ser un archivo regular.", mid=mid))
                from .catalog import _digest
                digest = _digest(path)
        except OSError as error:
            raise ValueError(diagnostic("Material {mid} no accesible: {path}.", mid=mid, path=material['path'])) from error
        if digest != material["sha256"]:
            raise ValueError(diagnostic("El material {mid} ha cambiado: revisar su banco antes de usarlo.", mid=mid))

    def material(self, mid, material, label):
        declared = material.get("path")
        material_id = material.get("material_id", mid if _uuid(mid) else None)
        record = None
        if self.v4 and (material_id is not None or "content_version" in material):
            record = self.records.get(material_id) if isinstance(material_id, str) else None
            if not record or record["kind"] != "file" or record.get("presence") != "present":
                raise ValueError(diagnostic("{label}: identidad ausente o pendiente de reconciliar.", label=label))
            version = material.get("content_version")
            if type(version) is not int or version != record["content_version"]:
                raise ValueError(diagnostic("{label}: versión distinta o ausente; revisar el banco.", label=label))
            # La ruta guardada puede preceder a un movimiento. Nunca se lee a partir de ella.
            if declared is not None:
                _relative(self.root, declared, label)
            if material.get("sha256") != record["sha256"]:
                raise ValueError(diagnostic("{label}: la huella declarada no corresponde a la versión del catálogo.", label=label))
            declared = record["path"]
        path = _relative(self.root, declared, label)
        if self.v4:
            relative = self._check_boundary(path, internal=False)
            record = record or self.paths.get(relative)
            if relative in self.disputed or record and record.get("presence") != "present":
                raise ValueError(diagnostic("{label}: identidad pendiente de reconciliar.", label=label))
            if (material["access"] == "estudiante" and (record or self._generated(relative))
                    and (record or {}).get("access") != "estudiante"):
                raise ValueError(diagnostic("{label}: el catálogo reserva este material al docente.", label=label))
            material["path"] = relative
            if path in self.direct:
                return path
        if self.config is not None and not source_allowed(self.root, self.config, path):
            raise ValueError(diagnostic("{label}: fuente no seleccionada o excluida: {declared}.", label=label, declared=declared))
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
            raise ValueError(diagnostic("Metadatos no válidos para {qid}.", qid=qid))
        present = {field for field in ("family_id", "variant_id") if field in info}
        if not present:
            continue
        if len(present) != 2:
            raise ValueError(diagnostic("{qid}: family_id y variant_id deben declararse juntos.", qid=qid))
        family = _text(info["family_id"], diagnostic("family_id de {qid}", qid=qid))
        variant = _text(info["variant_id"], diagnostic("variant_id de {qid}", qid=qid))
        concepts = _strings(info.get("concepts"), diagnostic("Conceptos de {qid}", qid=qid))
        objective = _text(info.get("objective"), diagnostic("Objetivo de {qid}", qid=qid))
        if not isinstance(info.get("difficulty"), str) or info["difficulty"] not in DIFFICULTIES:
            raise ValueError(diagnostic("Dificultad no válida en {qid}.", qid=qid))
        signature = (frozenset(concepts), objective, info["difficulty"])
        variants, expected = families.setdefault(family, (set(), signature))
        if variant in variants:
            raise ValueError(diagnostic("Variante duplicada {variant} en familia {family}.", variant=variant, family=family))
        if signature != expected:
            raise ValueError(diagnostic("Familia {family}: las variantes deben compartir conceptos, objetivo y dificultad.", family=family))
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


def _check_metadata(metadata: dict, bank: list[dict], inputs: _BankInputs):
    materials = metadata.get("materials")
    entries, concepts = metadata.get("questions"), metadata.get("concepts")
    if not isinstance(materials, dict) or not materials:
        raise ValueError(diagnostic("Los metadatos del catálogo requieren materials no vacío."))
    if not isinstance(entries, dict) or not isinstance(concepts, dict) or not concepts:
        raise ValueError(diagnostic("Los metadatos requieren questions y concepts no vacíos."))
    if set(entries) != {q["id"] for q in bank}:
        raise ValueError(diagnostic("Cada pregunta del banco debe tener sus metadatos, sin IDs adicionales."))
    # First validate all paths and permissions, before reading any original.
    checked_paths = {}
    original_paths = {}
    for mid, material in materials.items():
        _text(mid, diagnostic("Identificador de material"))
        if not isinstance(material, dict):
            raise ValueError(diagnostic("Material no válido: {mid}.", mid=mid))
        _text(material.get("title"), diagnostic("Título del material {mid}", mid=mid))
        if material.get("access") not in ("estudiante", "docente"):
            raise ValueError(diagnostic("Acceso no válido en material {mid}.", mid=mid))
        if not isinstance(material.get("sha256"), str) or not _SHA.fullmatch(material["sha256"]):
            raise ValueError(diagnostic("Huella SHA-256 no válida en material {mid}.", mid=mid))
        saved = material.get("path")
        checked_paths[mid] = inputs.material(mid, material, f"Material {mid}")
        if saved is not None:
            original_paths.setdefault(saved, set()).add(checked_paths[mid])
    declared_access = {}
    for mid, material in materials.items():
        path = checked_paths[mid]
        if path in declared_access and declared_access[path] != material["access"]:
            raise ValueError(diagnostic("Accesos contradictorios para el material {path}.", path=material['path']))
        declared_access[path] = material["access"]
    def check_references(entry, label):
        references = entry.get("references", [])
        if not isinstance(references, list):
            raise ValueError(diagnostic("references debe ser una lista en {label}.", label=label))
        for ref in references:
            if not isinstance(ref, dict) or ref.get("access") not in ("estudiante", "docente"):
                raise ValueError(diagnostic("Referencia no válida en {label}.", label=label))
            _text(ref.get("title"), diagnostic("Referencia de {label}", label=label))
            reference_id = ref.get("material_id")
            if reference_id is not None:
                if not isinstance(reference_id, str) or reference_id not in checked_paths:
                    raise ValueError(diagnostic("Referencia de {label} sin material declarado.", label=label))
                path = checked_paths[reference_id]
            else:
                saved = _text(ref.get("path"), diagnostic("Referencia de {label}", label=label))
                candidates = original_paths.get(saved, set())
                if len(candidates) > 1:
                    raise ValueError(diagnostic("Referencia de {label} ambigua. Indicar material_id.", label=label))
                path = next(iter(candidates)) if candidates else _relative(inputs.root, saved, label)
            if path not in declared_access:
                raise ValueError(diagnostic("La referencia de {label} debe apuntar a un material declarado.", label=label))
            if declared_access[path] != ref["access"]:
                raise ValueError(diagnostic("La referencia de {label} contradice el acceso del material.", label=label))
            ref["path"] = path.relative_to(inputs.root).as_posix()

    for cid, concept in concepts.items():
        _text(cid, diagnostic("Identificador de concepto"))
        if not isinstance(concept, dict):
            raise ValueError(diagnostic("Concepto no válido: {cid}.", cid=cid))
        _text(concept.get("label"), diagnostic("Etiqueta del concepto {cid}", cid=cid))
        check_references(concept, diagnostic("concepto {cid}", cid=cid))
    for qid, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(diagnostic("Metadatos no válidos para {qid}.", qid=qid))
        if any(cid not in concepts for cid in _strings(entry.get("concepts"), diagnostic("Conceptos de {qid}", qid=qid))):
            raise ValueError(diagnostic("Concepto no declarado en {qid}.", qid=qid))
        _text(entry.get("objective"), diagnostic("Objetivo de {qid}", qid=qid))
        _text(entry.get("guidance"), diagnostic("Orientación de repaso de {qid}", qid=qid))
        if not isinstance(entry.get("difficulty"), str) or entry["difficulty"] not in DIFFICULTIES:
            raise ValueError(diagnostic("Dificultad no válida en {qid}.", qid=qid))
        refs = entry.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError(diagnostic("source_refs es obligatorio en {qid}.", qid=qid))
        seen = set()
        for ref in refs:
            if (not isinstance(ref, dict) or not isinstance(ref.get("material_id"), str)
                    or ref["material_id"] not in materials):
                raise ValueError(diagnostic("Material no declarado en source_refs de {qid}.", qid=qid))
            if ref["material_id"] in seen:
                raise ValueError(diagnostic("Material repetido en source_refs de {qid}.", qid=qid))
            seen.add(ref["material_id"])
            _strings(ref.get("locators"), diagnostic("Localizadores de {qid}", qid=qid))
        check_references(entry, diagnostic("pregunta {qid}", qid=qid))
    validate_variants(metadata, bank)
    for mid, path in checked_paths.items():
        inputs.check_digest(mid, path, materials[mid])


def _course_file(location, role, project_root, direct_materials=None):
    supplied = Path(os.path.abspath(Path(location).expanduser()))
    path = supplied.resolve()
    discovered_root = find_project(supplied.parent) or find_project(path.parent)
    root = (Path(project_root).expanduser().resolve() if project_root is not None
            else discovered_root or path.parent)
    if project_root is not None and discovered_root is not None and discovered_root != root:
        raise ValueError(diagnostic("El catálogo y la raíz indicada pertenecen a proyectos diferentes."))
    is_course = discovered_root == root or (project_root is not None and find_project(root) == root)
    config = load_project(root) if is_course else None
    inputs = _BankInputs(root, config, direct_materials)
    if inputs.v4:
        # Conservar la ruta introducida bajo el curso incluso en /var y /tmp de macOS.
        for ancestor in supplied.parents:
            if ancestor.resolve() == root:
                supplied = root / supplied.relative_to(ancestor)
                break
        inputs.check_bank_file(supplied, role)
    return path, root, discovered_root, inputs


@with_diagnostics
def validate_course_bank_files(gift_path, metadata_path=None, *, project_root=None, language=None):
    """Comprobar un banco GIFT suelto antes de abrirlo en un curso con espacios."""
    _course_file(gift_path, "gift", project_root)
    if metadata_path is not None:
        _course_file(metadata_path, "metadata", project_root)


def load_catalog(catalog_path: str | Path, *, project_root=None, bank_ids=None, direct_materials=None) -> dict:
    """Cargar bancos seleccionados con metadatos y originales congelables.

    La API pública de diagnóstico es validate_catalog. Este resultado interno
    incluye bytes para construir snapshots sin volver a leer archivos mutables.
    """
    path, root, discovered_root, inputs = _course_file(catalog_path, "catalog", project_root, direct_materials)
    catalog, catalog_raw = _json_bytes(path)
    path_base = catalog.get("path_base", "catalog")
    if path_base not in ("catalog", "project"):
        raise ValueError(diagnostic("path_base debe ser 'catalog' o 'project'."))
    if path_base == "project" and project_root is None and discovered_root is None:
        raise ValueError(diagnostic("path_base project requiere --project o un proyecto-docente.json cercano."))
    bank_root = root if path_base == "project" else path.parent
    rows = catalog.get("banks")
    if not isinstance(rows, list) or not rows:
        raise ValueError(diagnostic("El catálogo requiere una lista banks no vacía."))
    by_id, gift_paths = {}, set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not _BANK_ID.fullmatch(row["id"]):
            raise ValueError(diagnostic("Cada banco requiere un id estable en minúsculas, sin espacios."))
        if row["id"] in by_id:
            raise ValueError(diagnostic("Identificador de banco duplicado: {id}.", id=row['id']))
        by_id[row["id"]] = row
        for key in ("gift", "metadata"):
            _relative(bank_root, row.get(key), diagnostic("{key} de {id}", key=key, id=row['id']))
        gift_path = _relative(bank_root, row["gift"], diagnostic("GIFT de {id}", id=row['id']))
        if gift_path in gift_paths:
            raise ValueError(diagnostic("El catálogo registra el mismo archivo GIFT más de una vez."))
        gift_paths.add(gift_path)
    selected_ids = list(by_id) if bank_ids is None else _strings(bank_ids, diagnostic("Bancos seleccionados"))
    if set(selected_ids) - set(by_id):
        raise ValueError(diagnostic("La selección contiene bancos que no existen en el catálogo."))
    combined, originals = [], []
    merged = {"schema_version": 1, "materials": {}, "questions": {}, "concepts": {}}
    for bid in selected_ids:
        row = by_id[bid]
        gift_path = _relative(bank_root, row["gift"], diagnostic("GIFT de {bid}", bid=bid))
        metadata_path = _relative(bank_root, row["metadata"], diagnostic("Metadatos de {bid}", bid=bid))
        inputs.check_bank_file(gift_path, "gift")
        inputs.check_bank_file(metadata_path, "metadata")
        try:
            raw = gift_path.read_bytes()
            bank = parse_gift(raw.decode("utf-8-sig"))
        except (OSError, UnicodeError) as error:
            raise ValueError(diagnostic("No se puede leer el banco {bid}: {error}", bid=bid, error=error)) from error
        if not bank:
            raise ValueError(diagnostic("El banco {bid} está vacío.", bid=bid))
        metadata, metadata_raw = _json_bytes(metadata_path)
        _check_metadata(metadata, bank, inputs)
        for section in ("materials", "concepts"):
            for key, item in metadata[section].items():
                if key in merged[section] and merged[section][key] != item:
                    raise ValueError(diagnostic("Declaraciones contradictorias de {section}/{key} entre bancos.", section=section, key=key))
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
            raise ValueError(diagnostic("Accesos contradictorios entre bancos: {path}.", path=material['path']))
        access_by_path[key] = material["access"]
    return {"bank": combined, "metadata": merged, "banks": originals,
            "catalog": catalog, "catalog_bytes": catalog_raw}


@with_diagnostics
def validate_catalog(catalog_path: str | Path, *, project_root=None, direct_materials=None, language=None) -> dict:
    """Validar catálogo, metadatos, permisos y huellas; no escribir archivos."""
    loaded = load_catalog(catalog_path, project_root=project_root, direct_materials=direct_materials)
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
    _strings(selection.get("banks"), diagnostic("Bancos seleccionados"))
    quotas = selection.get("quotas")
    if not isinstance(quotas, list) or not quotas:
        raise ValueError(diagnostic("La selección requiere quotas no vacías."))
    labels = set()
    for quota in quotas:
        if not isinstance(quota, dict):
            raise ValueError(diagnostic("Cada cuota debe ser un objeto."))
        label = _text(quota.get("label"), diagnostic("Etiqueta de cuota"))
        if label in labels:
            raise ValueError(diagnostic("Etiqueta de cuota duplicada: {label}.", label=label))
        labels.add(label)
        if type(quota.get("count")) is not int or quota["count"] < 1:
            raise ValueError(diagnostic("La cuota {label} requiere count entero positivo.", label=label))
        if set(quota) - {"label", "count", "material_ids", "concepts", "difficulty", "types"}:
            raise ValueError(diagnostic("Filtro desconocido en la cuota {label}.", label=label))
        for field in ("material_ids", "concepts", "types"):
            if field in quota:
                _strings(quota[field], diagnostic("{field} de {label}", field=field, label=label))
        if "difficulty" in quota and (not isinstance(quota["difficulty"], str) or quota["difficulty"] not in DIFFICULTIES):
            raise ValueError(diagnostic("Dificultad no válida en cuota {label}.", label=label))
        if "types" in quota and set(quota["types"]) - PRINT_TYPES:
            raise ValueError(diagnostic("Tipos no imprimibles o desconocidos en cuota {label}.", label=label))
    if sum(quota["count"] for quota in quotas) != questions:
        raise ValueError(diagnostic("La suma de cuotas debe coincidir con --questions."))
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
            raise ValueError(diagnostic("Fondo insuficiente para cumplir simultáneamente las cuotas sin repetir preguntas principales/familias; revisar su solapamiento o ampliar los bancos."))
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
                raise ValueError(diagnostic("La cuota {label} referencia {field} no declarados.", label=quota['label'], field=field))
    candidates = [[q["id"] for q in bank if _eligible(q, metadata["questions"][q["id"]], quota)]
                  for quota in quotas]
    for quota, pool in zip(quotas, candidates):
        if len(pool) < quota["count"]:
            raise ValueError(diagnostic("Fondo insuficiente en {label}: {available} preguntas compatibles para {count} solicitadas.", label=quota['label'], available=len(pool), count=quota['count']))
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
            raise ValueError(diagnostic("Tipo GIFT no serializable: {kind}.", kind=kind))
        if "feedback" in question:
            body += "\n####" + escape_gift(question["feedback"])
        chunks.append(f"::{escape_gift(question['id'])}::[{question['format']}]"
                      f"{escape_gift(question['prompt'])} {{\n{body}\n}}")
    text = "\n\n".join(chunks) + "\n"
    if parse_gift(text) != ordered:
        raise ValueError(diagnostic("La serialización del banco combinado ha alterado sus preguntas."))
    return text.encode("utf-8")
