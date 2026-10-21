#!/usr/bin/env python3
"""Build an offline HTML graph from explicit Markdown links in a v2 library."""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

if __package__:
    from .validate_library import _links, registry_path, validate_library
else:
    from validate_library import _links, registry_path, validate_library


MARKER = "<!-- asistente-docente:generated-graph:v1 -->"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "graph.html"
HOUSEKEEPING = {"index.md", "LEEME.md", "incidencias.md", "log.md"}
KIND_MAP = {"diapositivas": "presentacion", "cuestionario": "evaluacion", "examen": "evaluacion", "rubrica": "evaluacion"}


class GraphError(ValueError):
    """Invalid library or unsafe graph destination; no graph was generated."""


def _destination(markdown, target):
    if target.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    path = unquote(urlsplit(target).path)
    path = re.sub(r"\\([() ])", r"\1", path)
    return (markdown.parent / path).resolve() if path else None


def _href(path, output):
    return quote(Path(os.path.relpath(path, output.parent)).as_posix(), safe="/.-_")


def _make_payload(guide, registry, output, audience):
    roots = {key: (guide / relative).resolve() for key, relative in registry["source_roots"].items()}
    nodes, paths, dependencies, blocked = {}, {}, {}, set()
    housekeeping = {(guide / name).resolve() for name in HOUSEKEEPING}
    protected = housekeeping | {registry_path(guide).resolve(), TEMPLATE.resolve()}
    for source in registry["sources"]:
        identifier = "source:" + source["id"]
        original = (roots[source["root"]] / source["path"]).resolve()
        nodes[identifier] = {"id": identifier, "title": source["title"],
                             "kind": KIND_MAP.get(source["kind"], source["kind"]),
                             "access": source["access"], "reading": source["reading"],
                             "href": _href(original, output) if audience == "docente" else None}
        paths.setdefault(original, set()).add(identifier)
        protected.add(original)
    pages = {}
    for page in registry["pages"]:
        markdown = (guide / page["path"]).resolve()
        protected.add(markdown)
        if markdown in housekeeping:
            continue
        identifier = "page:" + page["path"]
        nodes[identifier] = {"id": identifier, "title": page["title"], "kind": page["kind"],
                             "access": page["access"], "reading": None,
                             "href": _href(markdown, output) if audience == "docente" else None,
                             "sourceIds": sorted("source:" + item for item in page["source_ids"])}
        paths.setdefault(markdown, set()).add(identifier)
        pages[identifier] = markdown
        dependencies[identifier] = set(nodes[identifier]["sourceIds"])
    edges = set()
    for identifier, markdown in pages.items():
        for target in _links(markdown.read_text(encoding="utf-8-sig")):
            destination = _destination(markdown, target)
            if destination is None or destination in housekeeping:
                continue
            targets = paths.get(destination)
            if not targets:
                # A local document without an access classification cannot be
                # used to establish that this page is safe for students.
                blocked.add(identifier)
                continue
            dependencies[identifier].update(targets)
            edges.update((identifier, target_id) for target_id in targets)
    if audience == "estudiante":
        blocked.update(identifier for identifier, node in nodes.items() if node["access"] != "estudiante")
        while True:
            additional = {identifier for identifier, targets in dependencies.items()
                          if identifier not in blocked and (targets & blocked or targets - nodes.keys())}
            if not additional:
                break
            blocked.update(additional)
        nodes = {identifier: node for identifier, node in nodes.items() if identifier not in blocked}
        edges = {(source, target) for source, target in edges if source in nodes and target in nodes}
    payload = {"schemaVersion": 1, "title": registry["title"] if audience == "docente"
               else "Mapa de materiales para estudiantes", "audience": audience,
               "nodes": [nodes[key] for key in sorted(nodes)],
               "edges": [{"source": source, "target": target} for source, target in sorted(edges)]}
    return payload, protected


def _wiki_links(payload, registry, graph_output, wiki_output):
    """Attach actual page documents without inventing conceptual graph edges."""
    if __package__:
        from .build_wiki import document_href
    else:
        from build_wiki import document_href
    page_nodes = {node["id"]: node for node in payload["nodes"] if node["id"].startswith("page:")}
    documents = {identifier: {"title": node["title"],
                             "href": document_href(identifier[5:], graph_output, wiki_output),
                             "markdownHref": node["href"]}
                 for identifier, node in page_nodes.items()}
    associated = {node["id"]: set() for node in payload["nodes"]}
    for identifier, node in page_nodes.items():
        associated[identifier].add(identifier)
        for source in node["sourceIds"]:
            if source in associated:
                associated[source].add(identifier)
    # Page/source metadata and actual links both provide document navigation.
    # Neither mechanism creates new conceptual edges in the graph.
    for edge in payload["edges"]:
        for origin, target in ((edge["source"], edge["target"]), (edge["target"], edge["source"])):
            if target in documents:
                associated[origin].add(target)
    for source in registry["sources"]:
        identifier = "source:" + source["id"]
        page = "page:" + (source.get("page") or "")
        if page in documents and identifier in associated:
            associated[identifier].add(page)
    for node in payload["nodes"]:
        identifiers = sorted(associated[node["id"]],
                             key=lambda key: (key != node["id"], documents[key]["title"], key))
        node["wikiDocuments"] = [documents[key] for key in identifiers]
    payload["wikiHref"] = document_href("index.md", graph_output, wiki_output)


def build_graph(guide_dir, output, audience="docente", wiki_output=None):
    """Validate, filter and write one standalone HTML; return visible counts.

    Existing files are replaced only when they start with this generator's
    marker. Registered source/page files and the template are always protected.
    Student exports contain only permitted nodes, with no file links or hidden
    records. Metadata provenance affects privacy but never creates graph edges.
    """
    if audience not in {"docente", "estudiante"}:
        raise GraphError("audience debe ser docente o estudiante.")
    if audience == "estudiante" and wiki_output is not None:
        raise GraphError("El lector de la wiki es de uso docente; no se incluye en el grafo para estudiantes.")
    try:
        guide = Path(guide_dir).expanduser().resolve()
        validation = validate_library(guide)
        if validation["status"] != "ok":
            raise GraphError("Biblioteca inválida: " + "; ".join(validation["errors"]))
        registry = json.loads(registry_path(guide).read_text(encoding="utf-8-sig"))
        if not isinstance(registry, dict) or registry.get("schema_version") != 2:
            raise GraphError("El grafo requiere fuentes.json schema_version 2. Migra y revisa el registro antes de generarlo.")
        requested = Path(output).expanduser()
        if requested.is_symlink():
            raise GraphError("La salida no puede ser un enlace simbólico.")
        destination = requested.resolve()
        if destination.suffix.lower() != ".html":
            raise GraphError("La salida debe ser un archivo .html.")
        if not destination.parent.is_dir():
            raise GraphError("La carpeta de salida debe existir antes de generar el grafo.")
        payload, protected = _make_payload(guide, registry, destination, audience)
        if destination in protected:
            raise GraphError("La salida coincide con un original, una página o un archivo de entrada protegido.")
        existing = None
        if destination.exists():
            existing = destination.read_text(encoding="utf-8")
            if not existing.startswith(MARKER + "\n"):
                raise GraphError("El archivo de salida ya existe y no fue generado por esta utilidad.")
        template = TEMPLATE.read_text(encoding="utf-8")
        if template.count("__GRAPH_DATA__") != 1 or not template.startswith(MARKER + "\n"):
            raise GraphError("La plantilla de grafo no contiene el contrato esperado.")
        wiki_summary = None
        if wiki_output is not None:
            if __package__:
                from .build_wiki import build_wiki
            else:
                from build_wiki import build_wiki
            wiki_destination = Path(wiki_output).expanduser().resolve()
            if wiki_destination == destination:
                raise GraphError("El lector de la wiki y el grafo necesitan archivos de salida diferentes.")
            wiki_summary = build_wiki(guide, wiki_output, graph=destination)
            _wiki_links(payload, registry, destination, wiki_destination)
        embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        embedded = embedded.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        rendered = template.replace("__GRAPH_DATA__", embedded)
        if rendered != existing:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                                 dir=destination.parent, prefix=".graph-", suffix=".tmp",
                                                 delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(rendered)
                # Recheck just before replacing to avoid overwriting a newly
                # created or concurrently changed file without authorization.
                if destination.exists():
                    if existing is None or destination.read_text(encoding="utf-8") != existing:
                        raise GraphError("La salida cambió durante la generación; no se sobrescribe.")
                    os.replace(temporary, destination)
                else:
                    os.link(temporary, destination)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        summary = {"status": "ok", "audience": audience, "output": str(destination),
                   "nodes": len(payload["nodes"]), "edges": len(payload["edges"])}
        if wiki_summary is not None:
            summary["wiki"] = wiki_summary
        return summary
    except GraphError:
        raise
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        raise GraphError(str(exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide_dir", metavar="GUIDE_DIR")
    parser.add_argument("--output", required=True, metavar="FILE")
    parser.add_argument("--audience", choices=("docente", "estudiante"), default="docente")
    parser.add_argument("--wiki-output", metavar="FILE", help="Generar también el lector docente, normalmente GUIDE_DIR/index.html.")
    args = parser.parse_args(argv)
    try:
        summary = build_graph(args.guide_dir, args.output, args.audience, args.wiki_output)
    except GraphError as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
