#!/usr/bin/env python3
"""Prueba opcional en navegador: distribución visible y accesos a la wiki.

    ASISTENTE_DOCENTE_CHROMIUM=/ruta/al/navegador python tests/check_graph_layout.py

Usa únicamente datos sintéticos y archivos temporales. No necesita red.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time

from check_graph_browser import load, state, write_fixture


def fixture(count=48):
    kinds = ["tema", "concepto", "presentacion", "practica"]
    nodes = [{"id": f"page:{i:04}", "title": f"{i + 1}. Evidencia y fuentes para interpretar el cambio",
              "kind": kinds[i % 4], "access": "estudiante", "href": f"ficha-{i}.md"}
             for i in range(count)]
    edges = [{"source": f"page:{i // 12 * 12:04}", "target": f"page:{i:04}", "label": "Fundamenta"}
             for i in range(count) if i % 12]
    nodes[0]["wikiDocuments"] = [
        {"title": "Interpretación de la evidencia", "href": "index.html#interpretacion", "markdownHref": "tema.md"},
        {"title": "Evaluación de referencia", "href": "index.html#evaluacion", "markdownHref": "evaluacion.md"},
        {"title": "Enlace inválido", "href": "javascript:alert(1)", "markdownHref": "data:text/html,error"},
    ]
    return {"schemaVersion": 1, "title": "Mapa sintético extenso", "audience": "docente",
            "wikiHref": "index.html", "nodes": nodes, "edges": edges}


def overlaps(page):
    return page.evaluate("""() => {
      const boxes=[...document.querySelectorAll('#nodes .node')].map(n=>({id:n.dataset.nodeId,b:n.getBoundingClientRect()}));
      const collisions=[];
      for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
        const a=boxes[i].b,b=boxes[j].b;
        if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)
          collisions.push([boxes[i].id,boxes[j].id]);
      }
      return collisions;
    }""")


def main():
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory(prefix="docencia-layout-") as tmp, sync_playwright() as pw:
        directory = Path(tmp)
        (directory / "index.html").write_text("<!doctype html><h1>Wiki renderizada</h1><p id='interpretacion'>Evidencia</p>", encoding="utf-8")
        (directory / "tema.md").write_text("# Evidencia\n", encoding="utf-8")
        data = fixture()
        target = write_fixture(directory, data, "grafo.html")
        launch = {"headless": True}
        if os.environ.get("ASISTENTE_DOCENTE_CHROMIUM"):
            launch["executable_path"] = os.environ["ASISTENTE_DOCENTE_CHROMIUM"]
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(viewport={"width": 1440, "height": 960}, reduced_motion="reduce")
        errors, requests = [], []
        context.on("request", lambda r: requests.append(r.url) if r.url.startswith(("http:", "https:")) else None)
        context.route("http://**/*", lambda route: route.abort())
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        load(page, target)
        assert page.locator("#reset-button").inner_text() == "Reorganizar"
        assert not overlaps(page), overlaps(page)
        initial = state(page)
        page.locator("#fit-button").click()
        assert state(page)["positions"] == initial["positions"], "Ajustar solo debe mover la cámara"
        page.locator('#node-list [data-node-id="page:0000"]').click()
        page.locator("#reset-button").click()
        assert state(page)["selectedId"] == "page:0000"
        assert state(page)["positions"] == initial["positions"], "La selección no cambia la geometría"
        assert page.locator("#wiki-documents li").count() == 2, "Rechazar destinos ejecutables"
        assert page.locator("#wiki-documents").inner_text().count("Abrir Markdown") == 2
        page.locator("#wiki-documents a").first.click()
        assert page.locator("h1").inner_text() == "Wiki renderizada", "Abrir el documento renderizado"
        page.go_back()
        page.wait_for_function("window.graphView")
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

        # Filtered nodes stop exerting forces; their stored positions stay intact.
        initial = state(page)
        page.locator("#filter-type-presentacion").uncheck()
        first_filter = state(page)
        first_hidden = set(initial["visibleIds"]) - set(first_filter["visibleIds"])
        assert all(initial["positions"][i] == first_filter["positions"][i] for i in first_hidden)
        page.locator("#filter-type-practica").uncheck()
        filtered = state(page)
        hidden = set(first_filter["visibleIds"]) - set(filtered["visibleIds"])
        assert all(first_filter["positions"][i] == filtered["positions"][i] for i in hidden)
        assert any(initial["positions"][i] != filtered["positions"][i] for i in filtered["visibleIds"])
        page.locator('#node-list [data-node-id="page:0000"]').click()
        page.locator("#reset-button").click()
        assert state(page)["visibleIds"] == filtered["visibleIds"]
        assert state(page)["selectedId"] == "page:0000"
        assert state(page)["positions"] == filtered["positions"]
        assert page.locator("#wiki-documents li").count() == 2, "La wiki no depende del filtro visual"
        assert not overlaps(page), overlaps(page)
        page.locator("#search-input").fill("1.")
        page.locator("#reset-button").click()
        assert page.locator("#search-input").input_value() == "1."
        page.locator("#search-clear").click()
        page.locator("#selection-close").click()
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not overlaps(page), overlaps(page)

        # Defense in depth: even malformed student payloads cannot expose links.
        data["audience"] = "estudiante"
        student = write_fixture(directory, data, "estudiante.html")
        page.set_viewport_size({"width": 1440, "height": 960})
        load(page, student)
        page.locator('#node-list [data-node-id="page:0000"]').click()
        assert not page.locator("#wiki-section").is_visible()
        assert not page.locator("#open-wiki").is_visible()
        assert page.locator("#wiki-documents a").count() == 0

        large = write_fixture(directory, fixture(600), "extenso.html")
        start = time.monotonic()
        load(page, large)
        assert len(state(page)["visibleIds"]) == 600
        assert time.monotonic() - start < 15, "El cálculo debe mantener un presupuesto acotado"
        assert page.evaluate("""() => {
          const frame=document.querySelector('#graph').getBoundingClientRect();
          return [...document.querySelectorAll('#nodes .node')].every(n=>{const b=n.getBoundingClientRect();
            return b.left>=frame.left && b.right<=frame.right && b.top>=frame.top && b.bottom<=frame.bottom;});
        }"""), "Ajustar debe encajar también mapas extensos"
        connected_data = fixture(320)
        connected_data["edges"] = [{"source": f"page:{(i - 1) // 3:04}", "target": f"page:{i:04}"}
                                   for i in range(1, 320)]
        connected = write_fixture(directory, connected_data, "conectado.html")
        start = time.monotonic()
        load(page, connected)
        assert len(state(page)["visibleIds"]) == 320
        assert time.monotonic() - start < 15
        assert not errors, errors
        assert not requests, requests
        browser.close()
    print("Reorganización visible y determinista, etiquetas separadas, Ajustar, enlaces wiki, móvil y 600 nodos verificados.")


if __name__ == "__main__":
    main()
