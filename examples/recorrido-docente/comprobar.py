#!/usr/bin/env python3
"""Reproducir el circuito sintético en una carpeta nueva fuera del plugin."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys

PLUGIN = Path(__file__).resolve().parents[2]


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_example(destination, *, pdf=False):
    destination = Path(destination).expanduser().resolve()
    if destination.exists() or destination.is_relative_to(PLUGIN):
        raise ValueError("El destino debe ser una carpeta nueva fuera del plugin.")
    destination.mkdir(parents=True)
    course = destination / "curso"
    shutil.copytree(Path(__file__).parent / "curso", course)
    # La copia de trabajo debe ser editable aunque la instalación sea de solo lectura.
    for path in [course, *course.rglob("*")]:
        path.chmod(path.stat().st_mode | stat.S_IWUSR | (stat.S_IXUSR if path.is_dir() else 0))
    cli = PLUGIN / "scripts/docencia.py"

    def call(*args):
        result = subprocess.run([sys.executable, str(cli), *map(str, args)],
                                cwd=destination, capture_output=True, text=True, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return json.loads(result.stdout)

    initialized = call("init-project", course)
    assert not initialized["wiki_created"]
    assert not list((course / "mapa-docente").iterdir())
    activity = course / "creados/actividades/medir-y-justificar"
    student_activity = activity / "alumnado"
    rendered = call("render-markdown", student_activity / "enunciado.md",
                    "--output", student_activity / "impresion", "--title", "Medir y justificar",
                    *([] if pdf else ["--html-only"]))
    if rendered["pdf"]:
        record_path = activity / "docente/actividad.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["files"]["statement"]["pdf"] = "../alumnado/impresion/enunciado.pdf"
        save(record_path, record)
    original = {p.relative_to(course).as_posix(): p.read_bytes()
                for p in course.rglob("*") if p.is_file()}
    catalog = course / "creados/bancos/catalogo.json"
    call("validate-catalog", catalog, "--project", course)
    exams = course / "creados/cuestionarios/fuentes-mediciones-evidencias"
    args = ["build-exams", "--catalog", catalog, "--selection",
            course / "creados/bancos/reparto-ejemplo.json", "--project", course,
            "--output", exams, "--title", "Fuentes, mediciones y evidencias",
            "--models", "3", "--questions", "6", "--seed", "42", "--layout", "curso-v2"]
    if not pdf:
        args.append("--html-only")
    call(*args)
    manifest_file = exams / "docente/manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    batch = course / "resultados/medir-y-justificar/ordinaria"
    for profile, csv_file in (("tarea", "hoja-tarea"), ("libro", "libro")):
        call("export-grades", batch / f"correccion/evaluacion-{profile}.json",
             "--input", batch / f"recibidos/{csv_file}.csv",
             "--config", batch / f"correccion/perfil-{profile}.json",
             "--output", batch / f"correccion/{profile}")

    exam_batch = course / "resultados/fuentes-mediciones-evidencias/ordinaria"
    (exam_batch / "recibidos").mkdir(parents=True)
    detailed = exam_batch / "recibidos/detalle-examen.csv"
    header = ["Usuario", "Modelo", "Estado"] + [f"P{n:02d}" for n in range(1, 7)]
    with detailed.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        for i, model in enumerate(manifest["models"], 1):
            # Dos fallos en un concepto, uno aislado en otro y aciertos: prioridad verificable.
            scores = ["0" if "critica-fuentes" in q["concepts"] else "1"
                      for q in model["questions"]]
            science = next(j for j, q in enumerate(model["questions"]) if "medicion" in q["concepts"])
            scores[science] = "0.5"
            writer.writerow([f"{i:03d}", model["id"], "No presentado" if i == 3 else "Finalizado",
                             *([""] * 6 if i == 3 else scores)])
    gradebook = exam_batch / "recibidos/libro-examen.csv"
    gradebook.write_text(
        "Usuario;Modelo;Nota examen;Comentario examen;Otra nota\n"
        "001;A;3,50;Comentario anterior;8,00\n"
        "002;B;6,25;;9,00\n"
        "003;C;;Comentario que se vaciará;7,00\n", encoding="utf-8")
    config = {
        "identifier_column": "Usuario", "model_column": "Modelo", "status_column": "Estado",
        "absent_values": ["No presentado"],
        "question_columns": {str(n): f"P{n:02d}" for n in range(1, 7)},
        "max_scores": {str(n): 1 for n in range(1, 7)},
        "feedback_priority": {"max_concepts": 3, "marked_threshold": 0.5, "min_evidence": 2},
        "gradebook": {"identifier_column": "Usuario", "model_column": "Modelo",
                      "grade_column": "Nota examen", "feedback_column": "Comentario examen",
                      "delimiter": ";"}
    }
    config_file = exam_batch / "correccion/perfil-feedback.json"
    save(config_file, config)
    call("build-feedback", manifest_file, "--input", detailed, "--gradebook", gradebook,
         "--config", config_file, "--output", exam_batch / "correccion/feedback")
    for relative, content in original.items():
        assert (course / relative).read_bytes() == content, f"Original modificado: {relative}"
    summary = {"status": "ok", "models": 3, "questions_per_model": 6,
               "structure": "curso-v2",
               "pdf_requested": pdf, "wiki_created": False,
               "activity_pdf_registered": bool(rendered["pdf"]),
               "originals_preserved": True,
               "outputs": [str(path.relative_to(destination).as_posix()) for path in (
                   exams, batch / "correccion/tarea", batch / "correccion/libro",
                   exam_batch / "correccion/feedback")]}
    save(destination / "comprobacion.json", summary)
    return summary


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--pdf", action="store_true", help="Exigir generación real de PDF con Chromium")
    args = parser.parse_args()
    print(json.dumps(run_example(args.destination, pdf=args.pdf), ensure_ascii=False, indent=2))
