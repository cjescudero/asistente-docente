#!/usr/bin/env python3
"""Optional offline reader interaction checks with an already installed browser.

ASISTENTE_DOCENTE_CHROMIUM may select a local Chromium executable. Screenshots
are optional and must be saved outside the plugin. No browser is downloaded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_wiki import build_wiki


def fixture(root):
    guide = root / "mapa"
    guide.mkdir()
    (root / "materiales").mkdir()
    (guide / "contenidos").mkdir()
    (guide / "reservado").mkdir()
    for name in ("LEEME.md", "incidencias.md", "log.md"):
        (guide / name).write_text("# " + name + "\n", encoding="utf-8")
    (guide / "index.md").write_text(
        '# Índice\n\n[Medición](contenidos/medición.md)\n\n![Remota](https://example.invalid/pixel.png)\n\n'
        '<script>window.PWNED=true</script>\n\n## Referencias\n\nContenido docente.\n', encoding="utf-8")
    (guide / "contenidos/medición.md").write_text(
        '# Medición\n\n## Observación\n\nUna medida.\n\n## Síntesis\n\nEvidencia cuantitativa.\n\n'
        '| Tipo de material | Documento | Utilidad |\n| --- | --- | --- |\n'
        '| Presentaciones | Medición | Contrastar procedimientos y resultados. |\n\n'
        '[Volver](../index.md)\n\n[Sección local](#síntesis)\n', encoding="utf-8")
    (guide / "reservado/examen.md").write_text('# Examen reservado\n\nSolución sintética.\n', encoding="utf-8")
    data = {"schema_version": 2, "title": "Mapa sintético · Navegación", "course": None,
            "source_roots": {"curso": "../materiales"}, "sources": [], "pages": [
                {"path": "contenidos/medición.md", "title": "Medición", "kind": "concepto", "access": "estudiante", "source_ids": []},
                {"path": "reservado/examen.md", "title": "Examen reservado", "kind": "evaluacion", "access": "docente", "source_ids": []}]}
    (guide / "fuentes.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    build_wiki(guide)
    return guide / "index.html"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="Optional real reader to open and capture")
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    if args.screenshots:
        args.screenshots = args.screenshots.resolve()
        if args.screenshots == ROOT or ROOT in args.screenshots.parents:
            parser.error("Las capturas deben quedar fuera del plugin.")
        args.screenshots.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory(prefix="wiki-browser-") as tmp, sync_playwright() as pw:
        reader = fixture(Path(tmp))
        launch = {"headless": True}
        if os.environ.get("ASISTENTE_DOCENTE_CHROMIUM"):
            launch["executable_path"] = os.environ["ASISTENTE_DOCENTE_CHROMIUM"]
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(viewport={"width": 1440, "height": 960}, reduced_motion="reduce")
        network, errors, dialogs = [], [], []
        context.on("request", lambda req: network.append(req.url) if req.url.startswith(("http:", "https:")) else None)
        context.route("http://**/*", lambda route: route.abort())
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
        page.goto(reader.resolve().as_uri())
        assert page.locator("#document h1").inner_text() == "Índice"
        assert page.evaluate("window.PWNED") is None
        assert page.locator("#graph-link").is_hidden()
        page.locator("#document a", has_text="Medición").click()
        page.wait_for_function("document.querySelector('#document h1').textContent === 'Medición'")
        assert page.locator("#source-link").get_attribute("href") == "contenidos/medici%C3%B3n.md"
        page.locator("#toc a", has_text="Síntesis").click()
        page.wait_for_function("new URLSearchParams(location.hash.slice(1)).get('section') === 'síntesis'")
        assert page.locator("#section-síntesis").is_visible()
        current = page.url
        page.locator(".skip").focus()
        page.locator(".skip").press("Enter")
        assert page.url == current
        assert page.evaluate("document.activeElement.id") == "reader-main"
        page.locator("#document a", has_text="Volver").click()
        page.wait_for_function("document.querySelector('#document h1').textContent === 'Índice'")
        page.go_back()
        page.wait_for_function("document.querySelector('#document h1').textContent === 'Medición'")
        page.reload()
        assert page.locator("#document h1").inner_text() == "Medición"
        page.locator("#search").fill("cuantitativa")
        assert page.locator("#page-nav .page-link").count() == 1
        assert page.locator("#page-nav .page-link").inner_text() == "Medición"
        page.locator("#search").fill("")
        page.locator("#kind").select_option("evaluacion")
        assert page.locator("#page-nav .page-link").count() == 1
        page.locator("#page-nav .page-link").click()
        page.wait_for_function("document.querySelector('#document h1').textContent === 'Examen reservado'")
        assert "Área reservada" in page.locator("#access").inner_text()
        page.locator("#kind").select_option("")
        page.locator("#search").fill("sin coincidencia 918273")
        assert page.locator("#page-nav .empty").is_visible()
        page.locator("#search").fill("")
        if args.screenshots:
            page.screenshot(path=str(args.screenshots / "wiki-sintetica-escritorio.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#sidebar").is_hidden()
        page.locator("#toggle-menu").click()
        assert page.locator("#sidebar").is_visible()
        page.locator('#page-nav [data-path="contenidos/medición.md"]').click()
        page.wait_for_function("document.querySelector('#document h1').textContent === 'Medición'")
        assert page.locator("#sidebar").is_hidden()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.locator("#document table").evaluate("el => el.scrollWidth > el.clientWidth")
        assert page.locator("#document table").evaluate("el => {el.scrollLeft=90; return el.scrollLeft > 0;}")
        if args.screenshots:
            page.screenshot(path=str(args.screenshots / "wiki-sintetica-movil.png"), full_page=True)
        if args.html:
            page.set_viewport_size({"width": 1440, "height": 960})
            page.goto(args.html.resolve().as_uri())
            assert page.locator("#document h1").count() >= 1
            assert page.locator("#graph-link").is_visible()
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "wiki-ejemplo-escritorio.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "wiki-ejemplo-movil.png"), full_page=True)
        assert not network, network
        assert not errors, errors
        assert not dialogs, dialogs
        browser.close()
    print("Wiki: navegación, anclas, historial, enlaces profundos, búsqueda, filtros, móvil y ausencia de red verificados.")


if __name__ == "__main__":
    main()
