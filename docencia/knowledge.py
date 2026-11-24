"""Vínculos de la wiki a identidades estables. Las síntesis revisadas las escribe el agente."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from .catalog import reconcile, transaction
from .project import _replace_config, _safe_path, load_project, source_allowed
from scripts.validate_library import registry_path


def _relative(path, base):
    return Path(os.path.relpath(path, base)).as_posix()


def _source_path(guide, data, source):
    return (guide / data["source_roots"][source["root"]] / source["path"]).resolve()


def register_dependencies(root, guide):
    """Vincular únicamente un registro v2 previamente validado y el contenido realmente revisado."""
    data = json.loads(registry_path(guide).read_text(encoding="utf-8-sig"))
    if data.get("schema_version") != 2:
        raise ValueError("El catálogo de materiales requiere el registro v2 del mapa.")
    paths = {s["id"]: _source_path(guide, data, s).relative_to(root).as_posix() for s in data["sources"]}
    if paths:
        reconcile(root, scope=sorted(set(paths.values())))
    with transaction(root) as tx:
        records = {r["path"]: r for r in tx.data["materials"].values() if r["presence"] == "present"}
        bindings = {}
        for source in data["sources"]:
            path = paths[source["id"]]
            row = records.get(path)
            if not row or (source.get("sha256") and source["sha256"] != row["sha256"]):
                raise ValueError(f"Identidad o versión pendiente de revisión: {path}")
            bindings[source["id"]] = {"material_id": row["material_id"], "content_version": row["content_version"],
                                      "path": path}
        binding = {"map": guide.relative_to(root).as_posix(), "sources": bindings}
        if tx.data.get("wiki") != binding:
            tx.data["wiki"] = binding
            tx.event("register_wiki", map=binding["map"], sources=len(bindings))


# Solo se modifican los destinos de enlaces. Se preservan etiquetas, ejemplos de código y fragmentos.
_MARKUP = re.compile(r"(?P<code>(?P<ticks>`+)(?s:.*?)(?P=ticks))|"
                     r"(?P<start>!?\[[^\]\n]*\]\(\s*|^ {0,3}\[[^\]\n]+\]:\s*)"
                     r"(?P<dest><[^>\n]+>|(?:\\.|[^()\s]|\([^()\n]*\))+)", re.M)


def repair_markdown(text, old_parent, new_parent, moves):
    def replace(match):
        if match.group("code"):
            return match.group()
        raw = match["dest"].strip("<>")
        url = urlsplit(raw)
        if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
            return match.group()
        path = Path(os.path.abspath(old_parent / re.sub(r"\\([() ])", r"\1", unquote(url.path))))
        target = moves.get(path, path)
        if target == path and old_parent == new_parent:
            return match.group()
        rel = quote(_relative(target, new_parent), safe="/.-_")
        result = urlunsplit(("", "", rel, url.query, url.fragment))
        return match["start"] + ("<" + result + ">" if match["dest"].startswith("<") else result)

    # Proteger asimismo los bloques cercados con virgulillas o backticks de longitud variable.
    output, fence, block = [], None, []
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker and fence is None:
            output.append(_MARKUP.sub(replace, "".join(block)))
            block.clear()
            fence = marker[1]
        elif marker and fence and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
            output.append(line)
            fence = None
            continue
        if fence:
            output.append(line)
        else:
            block.append(line)
    output.append(_MARKUP.sub(replace, "".join(block)))
    return "".join(output)


def _dependent_pages(guide, registry, changed):
    from scripts.validate_library import _links
    direct = {p["path"] for p in registry["pages"] if changed.intersection(p["source_ids"])}
    if not direct:
        return []
    edges = {}
    for p in registry["pages"]:
        path = _safe_path(guide, p["path"])
        if not path.is_file():
            continue
        refs = set()
        for link in _links(path.read_text(encoding="utf-8-sig")):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if target.is_relative_to(guide):
                refs.add(target.relative_to(guide).as_posix())
        edges[p["path"]] = refs
    while True:
        extra = {p for p, refs in edges.items() if refs & direct} - direct
        if not extra:
            return sorted(direct)
        direct.update(extra)


def _pending_write(guide, path, old, new):
    if old == new:
        return None
    return {"path": path.relative_to(guide).as_posix(), "before": hashlib.sha256(old).hexdigest(),
            "after": hashlib.sha256(new).hexdigest(), "text": new.decode("utf-8")}


def _resume_links(tx, guide, binding):
    intent = binding.get("repair")
    if not intent:
        return
    for item in intent["files"]:
        path = _safe_path(guide, item["path"])
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if current == item["after"]:
            continue
        if current != item["before"]:
            raise ValueError(f"Cambió una página durante la reparación. Revisa {item['path']} antes de reanudar.")
        _replace_config(path, item["text"])
    for key, path in intent["destinations"].items():
        binding["sources"][key]["path"] = path
    binding["views_dirty"] = True
    del binding["repair"]
    tx.event("wiki_relocated", sources=sorted(intent["destinations"]))
    tx.flush()


def refresh_knowledge(root):
    """Reparación reintentable por identidad, incluso tras interrumpir el proceso posterior al traslado."""
    root = Path(root).resolve()
    config = load_project(root)
    if not config["map"]:
        return {"status": "no_map", "next": "Ofrecer crear el mapa con las fuentes elegidas."}
    from .spaces import corpus_policy
    config = {**config, "sources": corpus_policy(root, config)}
    guide = _safe_path(root, config["map"])
    registry_file = registry_path(guide)
    with transaction(root) as tx:
        binding = tx.data.get("wiki", {})
        if binding.get("map") != config["map"]:
            return {"status": "unregistered", "next": "Validar y registrar las dependencias del mapa existente."}
        _resume_links(tx, guide, binding)
        registry_before = registry_file.read_bytes()
        registry = json.loads(registry_before.decode("utf-8-sig"))
        bindings = binding["sources"]
        records = tx.data["materials"]
        selected = {r["material_id"] for r in records.values() if r["kind"] == "file" and r["presence"] == "present"
                    and source_allowed(root, config, root / r["path"])}
        available = selected - {b["material_id"] for b in bindings.values()}
        stale, moves = set(), {}
        moved = {}
        for source in registry["sources"]:
            key = source["id"]
            ref = bindings.get(key)
            if not ref or ref["material_id"] not in selected:
                stale.add(key)
                continue
            row = records[ref["material_id"]]
            if row.get("access_confirmed") and row["access"] != "estudiante" and source.get("access") == "estudiante":
                stale.add(key)
            if row["content_version"] != ref["content_version"]:
                stale.add(key)
            if ref["path"] == row["path"]:
                continue
            target = root / row["path"]
            moves[root / ref["path"]] = target
            moved[key] = row["path"]
            # Conservar la raíz elegida si sigue siendo adecuada, o registrar la del nuevo emplazamiento.
            base = (guide / registry["source_roots"][source["root"]]).resolve()
            if not target.is_relative_to(base):
                candidates = [r for r in config["sources"]["include"] if target.is_relative_to(root / r)]
                base = root / max(candidates, key=len)
                relative = _relative(base, guide)
                label = next((k for k, v in registry["source_roots"].items() if v == relative), None)
                if label is None:
                    label = "raiz-" + row["material_id"]
                    registry["source_roots"][label] = relative
                source["root"] = label
            source["path"] = target.relative_to(base).as_posix()
        affected = _dependent_pages(guide, registry, stale)
        if moves:
            # Registrar el texto final una sola vez. También permite reanudar un intercambio de nombres.
            changes = []
            for page in guide.rglob("*.md"):
                page = _safe_path(guide, page.relative_to(guide).as_posix())
                old = page.read_bytes()
                new = repair_markdown(old.decode("utf-8"), page.parent, page.parent, moves)
                change = _pending_write(guide, page, old, new.encode("utf-8"))
                if change:
                    changes.append(change)
            used = {s["root"] for s in registry["sources"]}
            registry["source_roots"] = {k: v for k, v in registry["source_roots"].items()
                                        if k in used or (guide / v).is_dir()}
            encoded = (json.dumps(registry, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            change = _pending_write(guide, registry_file, registry_before, encoded)
            if change:
                changes.append(change)
            binding["repair"] = {"files": changes, "destinations": moved}
            tx.event("wiki_relocating", sources=sorted(moved))
            tx.flush()
            _resume_links(tx, guide, binding)
        report = {"status": "review" if stale or available else "current", "changed_sources": sorted(stale),
                  "affected_pages": affected, "new_sources": sorted(available), "repaired_links_to": sorted(moved)}
        pending = {k: report[k] for k in ("changed_sources", "affected_pages", "new_sources")}
        if tx.data.get("wiki_pending") != pending:
            tx.data["wiki_pending"] = pending
            tx.event("wiki_review", **pending)
        if binding.get("views_dirty") and not stale:
            from scripts.build_graph import build_graph
            from scripts.build_wiki import build_wiki
            verified = {}
            for mid in selected:
                r = records[mid]
                signature = (r["physical_id"]["dev"], r["physical_id"]["ino"], r["size"], r["mtime_ns"])
                verified[root / r["path"]] = (signature, r["sha256"])
            reader, graph = guide / "index.html", guide / "grafo-docente.html"
            if graph.exists():
                build_graph(guide, graph, wiki_output=reader if reader.exists() else None, verified_files=verified)
            elif reader.exists():
                build_wiki(guide, reader, verified_files=verified)
            student = guide / "grafo-estudiante.html"
            if student.exists():
                build_graph(guide, student, audience="estudiante", verified_files=verified)
            binding.pop("views_dirty")
            tx.event("wiki_links_updated", sources=sorted(moved))
        return report
