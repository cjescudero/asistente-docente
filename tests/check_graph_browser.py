#!/usr/bin/env python3
"""Comprobación manual optativa del mapa, fuera de la suite unittest.

    .venv/bin/python tests/check_graph_browser.py
    .venv/bin/python tests/check_graph_browser.py --html /tmp/mapa/graph.html \
        --screenshots /tmp/mapa-capturas

Necesita Playwright y un navegador instalado. ASISTENTE_DOCENTE_CHROMIUM permite
indicar un ejecutable local. Solo escribe datos sintéticos temporales y capturas
en la ruta explícita; no modifica el HTML recibido ni la biblioteca.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MARKER = "__GRAPH_DATA__"


def fixture() -> dict:
    specs = [
        ("tema", "Medición y evidencia", "estudiante"),
        ("concepto", "Incertidumbre", "estudiante"),
        ("presentacion", "Introducción a la medición", "estudiante"),
        ("apuntes", "Guía de observación", "estudiante"),
        ("practica", "Práctica de contraste", "estudiante"),
        ("taller", "Taller de interpretación", "estudiante"),
        ("programa", "Programa de la asignatura", "estudiante"),
        ("evaluacion", "Rúbrica reservada", "docente"),
        ("otro", "Notas del profesor", "restringido"),
        ("concepto", "<img src=x onerror=alert(1)>", "estudiante"),
    ]
    nodes = [
        {"id": f"page:{i}", "title": title, "kind": kind, "access": access,
         "reading": None, "href": "javascript:alert(1)" if i == 9 else f"ficha-{i}.md"}
        for i, (kind, title, access) in enumerate(specs)
    ]
    return {
        "schemaVersion": 1, "title": "Biblioteca sintética · Ensayo", "audience": "docente",
        "nodes": nodes,
        "edges": [{"source": "page:0", "target": f"page:{i}", "label": "Se relaciona con"}
                  for i in range(1, len(nodes))],
    }


def write_fixture(directory: Path, data: dict, name: str) -> Path:
    template = (ROOT / "assets/graph.html").read_text(encoding="utf-8")
    assert template.count(MARKER) == 1, "El marcador debe aparecer una sola vez"
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    target = directory / name
    target.write_text(template.replace(MARKER, encoded), encoding="utf-8")
    return target


def state(page) -> dict:
    return page.evaluate("window.graphView.getState()")


def load(page, path: Path) -> None:
    page.goto(path.resolve().as_uri(), wait_until="load")
    page.wait_for_function("window.graphView && document.querySelector('#graph').clientWidth > 0")
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")


def check_interactions(page) -> None:
    assert page.locator("#audience-label").inner_text() == "Uso docente"
    assert not page.locator("#filter-type-evaluacion").is_checked()
    assert "page:7" not in state(page)["visibleIds"]
    page.locator("#filter-type-evaluacion").check()
    assert "page:7" in state(page)["visibleIds"]
    page.locator("#access-filters").locator("..").locator("summary").click()
    page.locator("#filter-access-restringido").uncheck()
    assert "page:8" not in state(page)["visibleIds"]
    page.locator("#filter-access-restringido").check()
    page.locator("#access-filters").locator("..").locator("summary").click()

    page.locator("#search-input").fill("MEDICION")
    assert set(state(page)["visibleIds"]) == {"page:0", "page:2"}, "Buscar sin tildes debe encontrar Medición"
    page.locator("#search-input").press("Enter")
    assert state(page)["selectedId"] == "page:0"
    assert page.locator("#selected-title").inner_text() == "Medición y evidencia"
    assert page.locator("#open-source").get_attribute("href").endswith("ficha-0.md")
    page.locator("#search-input").fill("sin coincidencias 293847")
    assert page.locator("#empty-state").is_visible()
    assert not state(page)["visibleIds"]
    page.locator("#show-all-button").click()
    assert len(state(page)["visibleIds"]) == 10

    item = page.locator('#node-list [data-node-id="page:1"]')
    item.focus()
    item.press("Enter")
    assert state(page)["selectedId"] == "page:1", "La lista debe permitir selección por teclado"
    page.locator('#relations-list [data-related-id="page:0"]').click()
    assert state(page)["selectedId"] == "page:0"
    page.locator("#selection-close").click()

    initial_zoom = state(page)["zoom"]
    page.locator("#zoom-in").click()
    assert state(page)["zoom"] > initial_zoom
    page.locator("#zoom-out").click()
    assert math.isclose(state(page)["zoom"], initial_zoom)
    page.locator("#fit-button").click()

    circle = page.locator('#nodes [data-node-id="page:0"] .node-core')
    box = circle.bounding_box()
    assert box, "Nodo principal visible"
    before = state(page)["positions"]["page:0"]
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 75, y + 35, steps=8)
    page.mouse.up()
    after = state(page)["positions"]["page:0"]
    assert math.hypot(after["x"] - before["x"], after["y"] - before["y"]) > 15, "Arrastrar debe mover el nodo"
    page.locator("#reset-button").click()
    reset = state(page)["positions"]["page:0"]
    assert math.isclose(reset["x"], before["x"]) and math.isclose(reset["y"], before["y"]), "Reorganizar debe ser reproducible para el mismo conjunto visible"

    graph_box = page.locator("#graph").bounding_box()
    assert graph_box
    x, y = graph_box["x"] + 16, graph_box["y"] + graph_box["height"] * 0.55
    hit = page.evaluate("([x,y]) => document.elementFromPoint(x,y)?.closest('[data-node-id]')?.dataset.nodeId || null", [x, y])
    assert hit is None, "El punto usado para el desplazamiento debe ser fondo"
    before_pan = state(page)["pan"]
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 40, y + 25, steps=5)
    page.mouse.up()
    assert state(page)["pan"] != before_pan, "Arrastrar el fondo debe desplazar el mapa"
    before_zoom = state(page)["zoom"]
    page.mouse.wheel(0, -120)
    page.wait_for_function("previous => window.graphView.getState().zoom > previous", arg=before_zoom)
    page.locator("#fit-button").click()

    page.locator('#node-list [data-node-id="page:9"]').click()
    assert page.locator("#selected-title").inner_text() == "<img src=x onerror=alert(1)>"
    assert page.locator("img").count() == 0, "Un título debe ser texto, no HTML"
    assert not page.locator("#open-source").is_visible(), "No abrir esquemas ejecutables"
    page.locator("#selection-close").click()


def check_mobile(page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#sidebar-toggle").click()
    assert page.locator("#sidebar-toggle").get_attribute("aria-expanded") == "true"
    page.locator("#search-input").fill("incertidumbre")
    page.locator('#node-list [data-node-id="page:1"]').click()
    assert page.locator("#selected-title").is_visible()
    assert page.locator("#sidebar-toggle").get_attribute("aria-expanded") == "false"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Sin desplazamiento horizontal en móvil"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="Mapa real adicional que abrir y capturar")
    parser.add_argument("--screenshots", type=Path, help="Directorio externo para capturas de escritorio y móvil")
    args = parser.parse_args()
    if args.html and not args.html.is_file():
        parser.error("--html debe apuntar a un archivo existente")
    if args.screenshots:
        destination = args.screenshots.resolve()
        if destination == ROOT or ROOT in destination.parents:
            parser.error("Las capturas deben guardarse fuera del paquete")
        destination.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory(prefix="docencia-graph-browser-") as temporary, sync_playwright() as pw:
        directory = Path(temporary)
        data = fixture()
        teacher = write_fixture(directory, data, "docente.html")
        launch = {"headless": True}
        if os.environ.get("ASISTENTE_DOCENTE_CHROMIUM"):
            launch["executable_path"] = os.environ["ASISTENTE_DOCENTE_CHROMIUM"]
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(viewport={"width": 1440, "height": 960}, reduced_motion="reduce")
        requests, errors, dialogs = [], [], []
        context.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        context.route("http://**/*", lambda route: route.abort())
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
        load(page, teacher)
        check_interactions(page)
        if args.screenshots:
            page.screenshot(path=str(args.screenshots / "sintetico-escritorio.png"), full_page=True)
        check_mobile(page)
        if args.screenshots:
            page.screenshot(path=str(args.screenshots / "sintetico-movil.png"), full_page=True)

        data["audience"] = "estudiante"
        data["nodes"] = [{**n, "href": None} for n in data["nodes"] if n["access"] == "estudiante"]
        ids = {n["id"] for n in data["nodes"]}
        data["edges"] = [e for e in data["edges"] if e["source"] in ids and e["target"] in ids]
        student = write_fixture(directory, data, "estudiante.html")
        page.set_viewport_size({"width": 1440, "height": 960})
        load(page, student)
        assert page.locator("#audience-label").inner_text() == "Vista del estudiante"
        assert "page:7" not in state(page)["visibleIds"] and "page:8" not in state(page)["visibleIds"]
        page.locator('#node-list [data-node-id="page:0"]').click()
        assert not page.locator("#open-source").is_visible()

        if args.html:
            load(page, args.html)
            assert page.locator("h1").inner_text() == "Mapa docente"
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "ejemplo-escritorio.png"), full_page=True)
            visible = state(page)["visibleIds"]
            if visible:
                page.locator("#node-list button").first.click()
                assert page.locator("#selected-title").is_visible()
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "ejemplo-movil.png"), full_page=True)
        assert not requests, f"No deben producirse solicitudes de red: {requests}"
        assert not errors, f"Errores JavaScript: {errors}"
        assert not dialogs, f"Contenido ejecutable inesperado: {dialogs}"
        browser.close()
    print("Mapa: filtros, búsqueda, teclado, enlaces, arrastre, zoom, móvil, estudiante y ausencia de red verificados.")


if __name__ == "__main__":
    main()
