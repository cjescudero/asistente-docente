#!/usr/bin/env python3
"""CLI portable. Ejecutable por ruta absoluta, sin instalación del paquete."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv=None):
    # Contrato UTF-8 también cuando Windows redirige stdout/stderr a una tubería.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Asistente docente: proyectos, bancos, exámenes y feedback.")
    commands = parser.add_subparsers(dest="command", required=True)
    project = commands.add_parser("init-project", help="Preparar un curso sin crear la wiki")
    project.add_argument("root", type=Path)
    selection = project.add_mutually_exclusive_group()
    selection.add_argument("--include", action="append", help="Carpeta relativa elegida; se puede repetir")
    selection.add_argument("--no-sources", action="store_true", help="Elegir explícitamente ninguna fuente")
    project.add_argument("--exclude", action="append", help="Archivo o subcarpeta relativa; sin patrones")
    project.add_argument("--dry-run", action="store_true")
    check = commands.add_parser("check-project", help="Diagnosticar estructura y entradas sin modificarlas")
    check.add_argument("root", type=Path)
    migration = commands.add_parser("plan-migration", help="Previsualizar movimientos y enlaces; nunca mover")
    migration.add_argument("root", type=Path)
    migration.add_argument("--moves", type=Path, required=True, help="Lista JSON de objetos from/to")
    register = commands.add_parser("register-map", help="Registrar un mapa real ya validado")
    register.add_argument("root", type=Path)
    register.add_argument("map_dir", type=Path)
    register.add_argument("--dry-run", action="store_true")
    bank = commands.add_parser("validate-bank", help="Validar un banco GIFT sin modificarlo")
    bank.add_argument("bank", type=Path)
    catalog = commands.add_parser("validate-catalog", help="Validar catálogo, procedencia y metadatos de bancos")
    catalog.add_argument("catalog", type=Path)
    catalog.add_argument("--project", type=Path, help="Raíz del curso para resolver materiales y selección")
    exam = commands.add_parser("build-exams", help="Generar modelos en papel y GIFT ofuscado")
    exam.add_argument("bank", type=Path, nargs="?")
    exam.add_argument("--catalog", type=Path)
    exam.add_argument("--selection", type=Path, help="Selección de bancos y cuotas de cobertura/dificultad")
    exam.add_argument("--project", type=Path, help="Raíz del curso del catálogo")
    exam.add_argument("--output", type=Path, required=True)
    exam.add_argument("--metadata", type=Path)
    exam.add_argument("--title", default="Evaluación")
    exam.add_argument("--models", type=int, default=2)
    exam.add_argument("--questions", type=int, default=5)
    exam.add_argument("--seed", type=int, default=42)
    exam.add_argument("--per-category", type=Path, help="JSON: categoría -> cantidad; suma --questions")
    exam.add_argument("--html-only", action="store_true")
    exam.add_argument("--layout", choices=("flat", "curso-v2"), default="flat",
                      help="curso-v2 separa alumnado y docente; flat conserva la salida anterior")
    feedback = commands.add_parser("build-feedback", help="Preparar comentarios CSV sin modificar notas")
    feedback.add_argument("manifest", type=Path)
    feedback.add_argument("--input", action="append", type=Path, required=True)
    feedback.add_argument("--config", type=Path, required=True)
    feedback.add_argument("--output", type=Path, required=True)
    feedback.add_argument("--detailed", action="store_true")
    feedback.add_argument("--consolidated", action="store_true")
    feedback.add_argument("--gradebook", type=Path, help="CSV de calificaciones para cruzar con el detalle")
    grades = commands.add_parser("export-grades", help="Comprobar una evaluación y preparar una copia de la hoja Moodle")
    grades.add_argument("evaluation", type=Path)
    grades.add_argument("--input", type=Path, required=True)
    grades.add_argument("--config", type=Path, required=True)
    grades.add_argument("--output", type=Path, required=True)
    markdown = commands.add_parser("render-markdown", help="Convertir Markdown a HTML autocontenido y PDF")
    markdown.add_argument("input", type=Path)
    markdown.add_argument("--output", type=Path, required=True)
    markdown.add_argument("--title")
    markdown.add_argument("--html-only", action="store_true")
    doctor = commands.add_parser("doctor", help="Comprobar capacidades locales sin instalar dependencias")
    doctor.add_argument("--pdf", action="store_true", help="Exigir también las capacidades PDF")
    doctor.add_argument("--project", type=Path, help="Añadir diagnóstico del curso")
    args = parser.parse_args(argv)
    if args.command == "build-exams":
        if bool(args.bank) == bool(args.catalog):
            parser.error("build-exams requiere un banco GIFT o --catalog, de forma excluyente.")
        if args.catalog and not args.selection:
            parser.error("--catalog requiere --selection con el reparto acordado.")
        if args.catalog and (args.metadata or args.per_category):
            parser.error("Con --catalog, los metadatos y las cuotas proceden del catálogo y --selection.")
        if not args.catalog and (args.selection or args.project):
            parser.error("--selection y --project requieren --catalog.")
    try:
        status = 0
        if args.command == "init-project":
            from docencia.project import initialize_project
            result = initialize_project(args.root, include=[] if args.no_sources else args.include,
                                        exclude=args.exclude, dry_run=args.dry_run)
            status = 2 if result["status"] == "pending_approval" else 0
        elif args.command == "check-project":
            from docencia.project import check_project
            result = check_project(args.root)
            status = {"ok": 0, "incomplete": 2, "invalid": 1}[result["status"]]
        elif args.command == "plan-migration":
            from docencia.project import plan_migration
            moves = json.loads(args.moves.read_text(encoding="utf-8-sig"))
            result = plan_migration(args.root, moves)
            status = 1 if result["status"] == "invalid" else 0
        elif args.command == "register-map":
            from docencia.project_map import register_map
            result = register_map(args.root, args.map_dir, dry_run=args.dry_run)
        elif args.command == "validate-bank":
            from docencia.gift import parse_gift
            questions = parse_gift(args.bank.read_text(encoding="utf-8-sig"))
            types = {}
            for question in questions:
                types[question["type"]] = types.get(question["type"], 0) + 1
            result = {"status": "ok", "questions": len(questions), "types": types}
        elif args.command == "validate-catalog":
            from docencia.banks import validate_catalog
            result = validate_catalog(args.catalog, project_root=args.project)
        elif args.command == "build-exams":
            from docencia.exams import build_exams
            quotas = json.loads(args.per_category.read_text(encoding="utf-8-sig")) if args.per_category else None
            manifest = build_exams(args.bank, args.output, title=args.title, models=args.models,
                                   questions=args.questions, seed=args.seed, metadata_path=args.metadata,
                                   per_category=quotas, html_only=args.html_only,
                                   catalog_path=args.catalog, selection_path=args.selection,
                                   project_root=args.project, layout=args.layout)
            statuses = {m["id"]: m["pdf_status"] for m in manifest["models"]}
            pending = any(str(s).startswith("PDF pendiente") for states in statuses.values() for s in states.values())
            manifest_dir = args.output.resolve() / "docente" if args.layout == "curso-v2" else args.output.resolve()
            result = {"status": "pdf_pending" if pending else "ok", "manifest": str(manifest_dir / "manifest.json"),
                      "excluded_question_ids": manifest["excluded_question_ids"], "pdf_status": statuses}
            status = 2 if pending else 0
        elif args.command == "build-feedback":
            from docencia.feedback import build_feedback
            result = build_feedback(args.manifest, args.input, args.config, args.output,
                                    detailed=args.detailed, consolidated=args.consolidated,
                                    gradebook_path=args.gradebook)
            status = 0 if result["status"] == "ok" else 1
        elif args.command == "export-grades":
            from docencia.grading import export_grades
            result = export_grades(args.evaluation, args.input, args.config, args.output)
            status = 0 if result["status"] == "ok" else 1
        elif args.command == "render-markdown":
            from docencia.render import render_markdown
            result = render_markdown(args.input, args.output, title=args.title, html_only=args.html_only)
            status = 2 if str(result["pdf_status"]).startswith("PDF pendiente") else 0
        else:
            from docencia.render import MATHJAX
            result = {"python": sys.version.split()[0], "python_supported": sys.version_info >= (3,10),
                      "mathjax": MATHJAX.is_file(), "markdown": bool(importlib.util.find_spec("markdown_it")),
                      "playwright": bool(importlib.util.find_spec("playwright")), "chromium": False}
            if result["playwright"]:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as playwright:
                    browser_path = os.environ.get("ASISTENTE_DOCENTE_CHROMIUM") or playwright.chromium.executable_path
                    result["chromium"] = Path(browser_path).is_file()
            result["basic_ready"] = all(result[k] for k in ["python_supported", "mathjax", "markdown"])
            result["pdf_ready"] = result["basic_ready"] and result["playwright"] and result["chromium"]
            status = 0 if result["pdf_ready" if args.pdf else "basic_ready"] else 2
            if args.project:
                from docencia.project import check_project
                result["project"] = check_project(args.project)
                result["project_tools_ready"] = result["python_supported"]
                if result["project"]["status"] == "invalid":
                    status = 1
                elif result["project"]["status"] != "ok" and status == 0:
                    status = 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return status
    except (ValueError, OSError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
