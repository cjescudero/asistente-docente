#!/usr/bin/env python3
"""Build a teacher-only, offline HTML reader from a validated Markdown map."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

if __package__:
    from .validate_library import _inside, registry_path, validate_library
else:
    from validate_library import _inside, registry_path, validate_library

MARKER = "<!-- asistente-docente:generated-wiki:v1 -->"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "wiki.html"
ADMIN_TITLES = {"index.md": "Índice general", "LEEME.md": "Convenciones de la guía",
                "incidencias.md": "Incidencias", "log.md": "Historial"}
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".bmp", ".ico"}


class WikiError(ValueError):
    """Invalid map or unsafe destination; input documents are never changed."""


def _href(path, output):
    return quote(Path(os.path.relpath(path, output.parent)).as_posix(), safe="/.-_")


def document_href(path, output, wiki_output):
    """Link from an HTML file to one registry-relative page in the wiki reader.

    ``path`` is a POSIX page path relative to GUIDE_DIR, including index.md.
    The stable fragment contract is #doc=<percent-encoded path>; an optional
    &section=<percent-encoded heading slug> may follow it.
    """
    return _href(Path(wiki_output).resolve(), Path(output).resolve()) + "#doc=" + quote(str(path), safe="")


def _route(path, fragment=""):
    result = "#doc=" + quote(path, safe="")
    return result + ("&section=" + quote(fragment, safe="") if fragment else "")


def _slug(value):
    value = unicodedata.normalize("NFKC", value).lower().strip()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"\s", "-", value) or "seccion"


def _markdown_renderer(markdown, page_path, output, known, roots, protected):
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise WikiError("Falta markdown-it-py. Instala las dependencias de requirements.txt.") from exc
    parser = MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")
    default_link = parser.renderer.rules.get("link_open")

    def rewrite(target, image=False):
        # Source HTML is escaped by markdown-it. Only explicitly listed URL
        # schemes may become links; all remote images remain inert until clicked.
        if not isinstance(target, str) or re.search(r"[\x00-\x1f\x7f]", target):
            return None
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            if not image and parts.scheme.lower() in {"https", "http", "mailto"}:
                return target
            return None
        relative = unquote(parts.path)
        if "\\" in relative or relative.startswith("/"):
            return None
        fragment = unquote(parts.fragment)
        if not relative:
            return _route(page_path, fragment) if not image else None
        destination = (markdown.parent / relative).resolve()
        if not any(_inside(destination, root) for root in roots):
            return None
        if destination != output:
            protected.add(destination)
        if destination in known and not image:
            return _route(known[destination], fragment)
        if image and destination.suffix.lower() not in RASTER_SUFFIXES:
            return None
        suffix = ("?" + parts.query if parts.query else "") + ("#" + quote(fragment, safe="-_.~") if fragment else "")
        return _href(destination, output) + suffix

    def link_open(tokens, idx, options, env):
        token = tokens[idx]
        target = rewrite(token.attrGet("href") or "")
        if target is None:
            token.attrs.pop("href", None)
            token.attrSet("class", "blocked-link")
            token.attrSet("title", "Destino no permitido en el visor")
        else:
            token.attrSet("href", target)
            if urlsplit(target).scheme:
                token.attrSet("rel", "noreferrer noopener")
                token.attrSet("target", "_blank")
        if default_link:
            return default_link(tokens, idx, options, env)
        return parser.renderer.renderToken(tokens, idx, options, env)

    def image_rule(tokens, idx, options, env):
        token = tokens[idx]
        target = rewrite(token.attrGet("src") or "", image=True)
        alt = html.escape(token.content, quote=True)
        if target is None:
            return '<span class="image-blocked">[Imagen no incorporada: ' + alt + "]</span>"
        title = token.attrGet("title")
        return '<img src="' + html.escape(target, quote=True) + '" alt="' + alt + '" loading="lazy"' + ((' title="' + html.escape(title, quote=True) + '"') if title else "") + ">"

    parser.renderer.rules["link_open"] = link_open
    parser.renderer.rules["image"] = image_rule
    return parser


def _page_record(page, guide, output, known, roots, protected):
    markdown = (guide / page["path"]).resolve()
    text = markdown.read_text(encoding="utf-8-sig")
    parser = _markdown_renderer(markdown, page["path"], output, known, roots, protected)
    tokens = parser.parse(text)
    used, headings = set(), []
    for idx, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        inline = tokens[idx + 1]
        label = "".join(child.content for child in inline.children or []
                        if child.type in {"text", "code_inline", "image"}) or inline.content
        base = _slug(label)
        slug, number = base, 1
        while slug in used:
            slug = base + "-" + str(number)
            number += 1
        used.add(slug)
        # Prefix HTML ids to isolate authored headings from the reader's UI IDs.
        token.attrSet("id", "section-" + slug)
        headings.append({"level": int(token.tag[1:]), "title": label, "slug": slug})
    return {"path": page["path"], "title": page["title"], "kind": page["kind"],
            "access": page["access"], "sourceHref": _href(markdown, output),
            "html": parser.renderer.render(tokens, parser.options, {}),
            "searchText": text, "headings": headings}


def build_wiki(guide_dir, output=None, graph=None):
    """Render registered v2 pages and the four administrative pages as one HTML.

    This is a teacher-only reader, including reserved documents. It never embeds
    original source documents, fetches URLs or exports a student copy. Only its
    own marked HTML may be replaced, atomically. All original files stay intact.
    """
    try:
        guide = Path(guide_dir).expanduser().resolve()
        validation = validate_library(guide)
        if validation["status"] != "ok":
            raise WikiError("Mapa inválido: " + "; ".join(validation["errors"]))
        registry = json.loads(registry_path(guide).read_text(encoding="utf-8-sig"))
        if registry.get("schema_version") != 2:
            raise WikiError("El visor requiere fuentes.json schema_version 2.")
        requested = Path(output).expanduser() if output is not None else guide / "index.html"
        if requested.is_symlink():
            raise WikiError("La salida no puede ser un enlace simbólico.")
        destination = requested.resolve()
        if destination.suffix.lower() != ".html" or not destination.parent.is_dir():
            raise WikiError("La salida debe ser un archivo .html en una carpeta existente.")
        roots = [guide] + [(guide / relative).resolve() for relative in registry["source_roots"].values()]
        protected = {registry_path(guide).resolve(), TEMPLATE.resolve(), Path(__file__).resolve()}
        protected.update((guide / registry["source_roots"][source["root"]] / source["path"]).resolve()
                         for source in registry["sources"])
        pages = [{"path": name, "title": title, "kind": "administracion", "access": "docente"}
                 for name, title in ADMIN_TITLES.items()] + sorted(registry["pages"], key=lambda page: page["path"])
        known = {(guide / page["path"]).resolve(): page["path"] for page in pages}
        protected.update(known)
        records = [_page_record(page, guide, destination, known, roots, protected) for page in pages]
        graph_path = Path(graph).expanduser().resolve() if graph is not None else None
        if graph_path is not None:
            if graph_path.suffix.lower() != ".html":
                raise WikiError("El grafo enlazado debe ser un archivo .html.")
            protected.add(graph_path)
        if destination in protected:
            raise WikiError("La salida coincide con un original, una página u otra entrada protegida.")
        existing = None
        if destination.exists():
            existing = destination.read_text(encoding="utf-8")
            if not existing.startswith(MARKER + "\n"):
                raise WikiError("La salida ya existe y no fue generada por esta utilidad.")
        template = TEMPLATE.read_text(encoding="utf-8")
        if not template.startswith(MARKER + "\n") or template.count("__WIKI_DATA__") != 1:
            raise WikiError("La plantilla del visor no contiene el contrato esperado.")
        payload = {"schemaVersion": 1, "title": registry["title"], "audience": "docente",
                   "index": "index.md", "graphHref": _href(graph_path, destination) if graph_path else None,
                   "documents": records}
        embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        embedded = embedded.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        rendered = template.replace("__WIKI_DATA__", embedded)
        if rendered != existing:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=destination.parent,
                                                 prefix=".wiki-", suffix=".tmp", delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(rendered)
                if destination.is_symlink():
                    raise WikiError("La salida se convirtió en enlace simbólico durante la generación.")
                if destination.exists():
                    if existing is None or destination.read_text(encoding="utf-8") != existing:
                        raise WikiError("La salida cambió durante la generación; no se sobrescribe.")
                    os.replace(temporary, destination)
                else:
                    os.link(temporary, destination)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        return {"status": "ok", "audience": "docente", "output": str(destination), "documents": len(records)}
    except WikiError:
        raise
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        raise WikiError(str(exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide_dir", metavar="GUIDE_DIR")
    parser.add_argument("--output", metavar="FILE", help="Predeterminado: GUIDE_DIR/index.html")
    parser.add_argument("--graph", metavar="FILE", help="Enlace de regreso a un grafo HTML docente")
    args = parser.parse_args(argv)
    try:
        result = build_wiki(args.guide_dir, args.output, args.graph)
    except WikiError as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
