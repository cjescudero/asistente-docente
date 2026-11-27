"""Run the bilingual example locally in a fresh directory, without an AI service."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parents[1]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(course, pdf=False):
    course = course.resolve()
    if course.is_relative_to(PLUGIN):
        raise ValueError("Choose a new directory outside the plugin.")
    course.mkdir(parents=True, exist_ok=False)

    def command(script, *args):
        result = subprocess.run([sys.executable, str(PLUGIN / "scripts" / script), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", cwd=course)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return json.loads(result.stdout)

    def cli(*args):
        return command("docencia.py", *args)

    sources = course / "Course materials"
    sources.mkdir()
    source = sources / "Mediciones.md"
    shutil.copyfile(HERE / source.name, source)
    cli("init-project", course, "--language", "en", "--include", sources.name)
    generated = course / "AI-generated materials"
    guide = generated / "Course map"
    topic = guide / "contenidos/measurement.md"
    topic.parent.mkdir(parents=True)
    topic.write_text("# Repeatability and calibration\n\nSimilar readings provide evidence of repeatability. "
                     "A consistent offset can survive averaging. Test calibration against a known mass. "
                     "[Mediciones en el aula, Repetibilidad y calibración](../../../Course%20materials/Mediciones.md).\n",
                     encoding="utf-8")
    for name, content in {"index.md": "# Measurement workshop\n\n[Read the topic](contenidos/measurement.md)",
                          "LEEME.md": "# Teacher guide\n\nSources retain their original titles.",
                          "incidencias.md": "# Review notes\n\nNo unresolved source issues.",
                          "log.md": "# Change log\n\nAdded the measurement reading."}.items():
        (guide / name).write_text(content + "\n", encoding="utf-8")
    page = {"title": "Repeatability and calibration", "path": "contenidos/measurement.md",
            "kind": "tema", "access": "estudiante", "source_ids": ["reading"]}
    reading = {"id": "reading", "root": "originals", "title": "Mediciones en el aula",
               "path": source.name, "kind": "apuntes", "course": None, "currency": "vigente",
               "access": "estudiante", "reading": "completa", "reviewed_locators": ["Repetibilidad y calibración", "Decisión experimental"],
               "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "page": page["path"]}
    write_json(guide / "_datos_internos/fuentes.json", {
        "schema_version": 2, "title": "Measurement workshop", "course": None,
        "source_roots": {"originals": "../../Course materials"}, "sources": [reading], "pages": [page]})
    command("build_wiki.py", guide)
    command("build_graph.py", guide, "--output", guide / "graph.html", "--audience", "teacher")
    cli("register-map", course, guide)

    activity = generated / "Scale workshop"
    students = activity / "students"
    teacher = activity / "teacher"
    students.mkdir(parents=True)
    teacher.mkdir()
    brief = students / "student-brief.md"
    shutil.copyfile(HERE / "materials/student-brief.md", brief)
    shutil.copyfile(HERE / "materials/teacher-rubric.md", teacher / "rubric.md")
    render_options = [] if pdf else ["--html-only"]
    cli("render-markdown", brief, "--output", students, *render_options)
    bank = generated / "Measurement bank"
    bank.mkdir()
    for name in ("workshop.gift", "metadata.json"):
        shutil.copyfile(HERE / "materials" / name, bank / name)
    cli("validate-bank", bank / "workshop.gift")
    quiz = generated / "Measurement quiz"
    built = cli("build-cuestionarios", bank / "workshop.gift", "--metadata", bank / "metadata.json",
                "--output", quiz, "--layout", "curso-v4", "--questions", "2", "--models", "1", *render_options)
    manifest = Path(built["manifest"])
    model = json.loads(manifest.read_text(encoding="utf-8"))["models"][0]
    assert model["language"] == "en"
    gift = (manifest.parent / model["files"]["gift"]).read_text(encoding="utf-8")
    assert "Question 01" in gift and "Answer A" in gift and "two grams" not in gift
    batch = course / "Student submissions" / "Measurement quiz"
    batch.mkdir()
    results = batch / "moodle.csv"
    results.write_text("Usuario;Modelo;Estado;P1;P2;Comentario;Nota\n001;A;Finalizado;0;0;;0,00\n", encoding="utf-8")
    profile = batch / "columns.json"
    write_json(profile, {"identifier_column": "Usuario", "model_column": "Modelo", "status_column": "Estado",
                         "feedback_column": "Comentario", "question_columns": {"1": "P1", "2": "P2"},
                         "max_scores": {"1": 1, "2": 1}, "absent_values": ["No presentado"], "blank_values": []})
    for language in ("en", "es"):
        destination = batch / language
        cli("build-feedback", manifest, "--input", results, "--config", profile,
            "--output", destination, "--language", language)
        output, = destination.glob("*.csv")
        with output.open(encoding="utf-8-sig", newline="") as stream:
            row = next(csv.DictReader(stream, delimiter=";"))
        if language == "es":
            assert "Calidad de la medición" in row["Comentario"] and "readings" not in row["Comentario"]
        else:
            assert "Measurement quality" in row["Comentario"] and "medición" not in row["Comentario"]
        assert row["Usuario"] == "001" and row["Nota"] == "0,00" and row["Comentario"]
    spanish_bank = bank / "calibracion.gift"
    spanish_bank.write_text("::01-A::¿Qué permite comprobar la calibración? "
                            "{=Una masa de referencia ~%-50%Repetir la misma lectura}\n", encoding="utf-8")
    spanish_quiz = generated / "Calibración"
    translated = cli("build-cuestionarios", spanish_bank, "--output", spanish_quiz,
                     "--questions", "1", "--models", "1", "--language", "es", *render_options)
    translated_manifest = Path(translated["manifest"])
    spanish_model = json.loads(translated_manifest.read_text(encoding="utf-8"))["models"][0]
    spanish_form = (translated_manifest.parent / spanish_model["files"]["student_html"]).read_text(encoding="utf-8")
    assert spanish_model["language"] == "es" and "Una masa de referencia" in spanish_form
    assert json.loads(manifest.read_text(encoding="utf-8"))["models"][0] == model
    return quiz


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course", type=Path)
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    print(run(args.course, args.pdf))
