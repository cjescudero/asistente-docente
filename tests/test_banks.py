"""Bancos de materiales sintéticos: procedencia, cuotas y snapshots."""
import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docencia.banks import serialize_bank, validate_catalog
from docencia.exams import build_exams
from docencia.gift import parse_gift
from docencia.project import initialize_project


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bancos-docentes-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = self.root / "catalogo.json"
        self.catalog_data = {"schema_version": 1, "banks": []}
        self.materials = {
            "texto": self.material("alumnado/materiales/texto.md", "Documento de historia", "estudiante"),
            "experimento": self.material("alumnado/actividades/experimento.md", "Registro experimental", "estudiante"),
            "examen": self.material("docente/fuentes/examen.md", "Examen anterior", "docente"),
        }
        self.concepts = {
            "evidencia": {"label": "Interpretar evidencias", "guidance": "Contrasta las evidencias.",
                         "references": [{"title": "Historia", "path": self.materials["texto"]["path"],
                                         "access": "estudiante"}]},
            "medicion": {"label": "Medición", "guidance": "Revisa el registro de medidas."},
        }
        self.add_bank("historia", "::repetida::[plain]La fuente es una carta.{FALSE#Error#Acierto}\n"
                                 "::historia-2::[plain]¿Cuál es una evidencia?{=Una carta~Una conjetura}")
        self.add_bank("ciencias", "::repetida::[plain]¿Cuál es el valor?{#1.23456789012345:0.00000000012345}\n"
                                 "::ciencia-2::[plain]La medida incluye unidades.{TRUE}",
                      concept="medicion", material="experimento")
        self.selection = self.root / "seleccion.json"
        self.select([{"label": "Humanidades", "count": 1, "material_ids": ["texto"]},
                     {"label": "Experimento", "count": 1, "concepts": ["medicion"]}])

    def save(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def material(self, relative, title, access):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(title + "\n", encoding="utf-8")
        return {"path": relative, "title": title, "access": access,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def add_bank(self, bid, gift, *, concept="evidencia", material="texto"):
        (self.root / f"{bid}.gift").write_text(gift + "\n", encoding="utf-8")
        metadata = {
            "schema_version": 1, "materials": copy.deepcopy(self.materials),
            "concepts": copy.deepcopy(self.concepts),
            "questions": {
                question["id"]: {
                    "source_refs": [{"material_id": material, "locators": ["sección 1"]}],
                    "concepts": [concept], "objective": "Interpretar un caso a partir de sus evidencias.",
                    "difficulty": "basica", "guidance": "Revisa la fuente y justifica la conclusión.",
                } for question in parse_gift(gift)
            },
        }
        self.save(self.root / f"{bid}.json", metadata)
        self.catalog_data["banks"].append({"id": bid, "gift": f"{bid}.gift", "metadata": f"{bid}.json"})
        self.save(self.catalog, self.catalog_data)
        return metadata

    def select(self, quotas, banks=None):
        self.save(self.selection, {"schema_version": 1,
                                  "banks": banks or [row["id"] for row in self.catalog_data["banks"]],
                                  "quotas": quotas})

    def build(self, target="out", **options):
        kwargs = {"models": 3, "questions": 2, "seed": 34, "html_only": True,
                  "catalog_path": self.catalog, "selection_path": self.selection}
        kwargs.update(options)
        return build_exams(None, self.root / target, **kwargs)

    def metadata(self, bid):
        path = self.root / f"{bid}.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_catalog_validates_sources_and_reports_serializable_counts(self):
        result = validate_catalog(self.catalog)
        self.assertEqual(result["questions"], 4)
        self.assertEqual(result["materials"], 3)
        self.assertEqual(result["status"], "ok")
        json.dumps(result)

    def test_same_original_id_in_different_banks_has_distinct_provenance(self):
        manifest = self.build(models=2, questions=4,
                              selection_path=self.selection_for_all())
        for model in manifest["models"]:
            self.assertEqual(len({q["source_id"] for q in model["questions"]}), 4)
            repeated = [q for q in model["questions"] if q["source_question_id"] == "repetida"]
            self.assertEqual({q["source_bank_id"] for q in repeated}, {"historia", "ciencias"})
            self.assertEqual({q["source_id"] for q in repeated}, {"historia::repetida", "ciencias::repetida"})
        parsed = parse_gift((self.root / "out/source/bank.gift").read_text(encoding="utf-8"))
        self.assertEqual({q["id"] for q in parsed}, set(manifest["metadata"]["questions"]))

    def selection_for_all(self):
        self.select([{"label": "Todas", "count": 4}])
        return self.selection

    def test_snapshots_are_byte_exact_frozen_and_do_not_copy_materials(self):
        self.catalog.write_bytes(b"\xef\xbb\xbf" + self.catalog.read_bytes())
        before = {f: f.read_bytes() for f in self.root.glob("*.json")}
        before.update({f: f.read_bytes() for f in self.root.glob("*.gift")})
        manifest = self.build()
        output = self.root / "out"
        for bank in manifest["source_banks"]:
            for field, suffix in (("gift", ".gift"), ("metadata", ".json")):
                raw = before[self.root / (bank["id"] + suffix)]
                self.assertEqual((output / bank[f"{field}_snapshot"]).read_bytes(), raw)
                self.assertEqual(bank[f"{field}_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual((output / manifest["catalog_snapshot"]).read_bytes(), before[self.catalog])
        self.assertEqual((output / manifest["selection_snapshot"]).read_bytes(), before[self.selection])
        self.assertFalse(list(output.rglob("*.md")))
        (self.root / "historia.gift").write_text("::cambio::Cambio{T}")
        self.assertEqual((output / "source/banks/historia.gift").read_bytes(),
                         before[self.root / "historia.gift"])
        self.assertEqual(json.loads((output / "manifest.json").read_text()), manifest)

    def test_all_models_have_same_quotas_and_reproduce_with_seed(self):
        manifest = self.build()
        self.assertEqual(manifest, self.build("again"))
        for model in manifest["models"]:
            self.assertEqual(model["coverage"]["quotas"], {"Humanidades": 1, "Experimento": 1})
            self.assertEqual(model["coverage"]["difficulty"], {"basica": 2})
        first_two = [q["source_id"] for model in manifest["models"][:2] for q in model["questions"]]
        self.assertEqual(len(set(first_two)), 4)
        report = manifest["selection_report"]
        self.assertEqual(report["pairwise_overlap"][0]["shared_questions"], 0)
        self.assertEqual(json.loads((self.root / "out/coverage.json").read_text()), report)

    def test_overlapping_quotas_use_augmenting_matching(self):
        path, metadata = self.metadata("historia")
        metadata["questions"]["repetida"]["concepts"].append("medicion")
        self.save(path, metadata)
        self.select([{"label": "Amplia", "count": 1, "concepts": ["evidencia"]},
                     {"label": "Estrecha", "count": 1, "concepts": ["medicion"]}],
                    banks=["historia"])
        for seed in range(10):
            manifest = self.build(f"overlap-{seed}", models=1, seed=seed)
            chosen = {q["quota_label"]: q["source_question_id"] for q in manifest["models"][0]["questions"]}
            self.assertEqual(chosen, {"Amplia": "historia-2", "Estrecha": "repetida"})

    def test_infeasible_overlap_reports_insufficiency_before_output(self):
        self.select([{"label": "A", "count": 2, "concepts": ["evidencia"]},
                     {"label": "B", "count": 1, "concepts": ["evidencia"]}])
        with self.assertRaisesRegex(ValueError, "simultáneamente"):
            self.build(questions=3)
        self.assertFalse((self.root / "out").exists())

    def test_filters_are_and_between_fields_and_or_inside_lists(self):
        path, metadata = self.metadata("historia")
        metadata["questions"]["repetida"]["difficulty"] = "avanzada"
        metadata["questions"]["repetida"]["source_refs"].append(
            {"material_id": "experimento", "locators": ["registro 2"]})
        self.save(path, metadata)
        self.select([{"label": "Cruce", "count": 1, "material_ids": ["experimento", "examen"],
                      "concepts": ["evidencia"], "difficulty": "avanzada", "types": ["truefalse"]}])
        manifest = self.build(questions=1, models=1)
        question = manifest["models"][0]["questions"][0]
        self.assertEqual(question["source_id"], "historia::repetida")
        self.assertEqual(len(question["source_refs"]), 2)

    def test_diagnoses_unknown_filters_and_insufficient_pool(self):
        cases = [
            [{"label": "Inexistente", "count": 2, "concepts": ["no-existe"]}],
            [{"label": "Insuficiente", "count": 2, "difficulty": "avanzada"}],
            [{"label": "Filtro mal escrito", "count": 2, "dificulty": "basica"}],
            [{"label": "Emparejamiento", "count": 2, "types": ["matching"]}],
            [{"label": "Menos preguntas", "count": 1}],
        ]
        for quotas in cases:
            self.select(quotas)
            with self.subTest(quotas=quotas), self.assertRaises(ValueError):
                self.build()
        self.assertFalse((self.root / "out").exists())

    def test_changed_material_blocks_new_exam_without_touching_existing_snapshot(self):
        manifest = self.build()
        snapshot = (self.root / "out/source/bank.gift").read_bytes()
        (self.root / self.materials["texto"]["path"]).write_text("Nueva versión")
        with self.assertRaisesRegex(ValueError, "ha cambiado"):
            self.build("changed")
        self.assertEqual((self.root / "out/source/bank.gift").read_bytes(), snapshot)
        self.assertEqual(hashlib.sha256(snapshot).hexdigest(), manifest["bank_sha256"])

    def test_excluded_material_is_not_opened(self):
        initialize_project(self.root, include=["alumnado", "docente/fuentes"],
                           exclude=["docente/fuentes/examen.md"])
        forbidden = (self.root / self.materials["examen"]["path"]).resolve()
        original = Path.read_bytes
        reads = []

        def checked(path):
            reads.append(path.resolve())
            if path.resolve() == forbidden:
                raise AssertionError("Se intentó leer el examen excluido.")
            return original(path)

        with patch.object(Path, "read_bytes", checked):
            with self.assertRaisesRegex(ValueError, "excluida"):
                self.build()
        self.assertNotIn(forbidden, reads)

    def test_reserved_exam_can_be_used_when_explicitly_selected(self):
        initialize_project(self.root, include=["alumnado", "docente/fuentes"])
        path, metadata = self.metadata("historia")
        metadata["questions"]["repetida"]["source_refs"] = [
            {"material_id": "examen", "locators": ["pregunta 1"]}]
        self.save(path, metadata)
        self.select([{"label": "Examen histórico", "count": 1, "material_ids": ["examen"]}])
        manifest = self.build(questions=1, models=1)
        self.assertEqual(manifest["models"][0]["questions"][0]["source_id"], "historia::repetida")
        student = (self.root / "out/modelo-A-student.html").read_text()
        self.assertNotIn("Examen anterior", student)
        self.assertNotIn("source_refs", student)

    def test_symlink_alias_to_excluded_source_is_rejected_before_read(self):
        initialize_project(self.root, include=["alumnado"], exclude=["docente/fuentes"])
        alias = self.root / "alumnado/materiales/alias.md"
        try:
            alias.symlink_to(self.root / self.materials["examen"]["path"])
        except (NotImplementedError, OSError) as error:
            self.skipTest(str(error))
        path, metadata = self.metadata("historia")
        metadata["materials"]["examen"]["path"] = "alumnado/materiales/alias.md"
        self.save(path, metadata)
        with self.assertRaisesRegex(ValueError, "simbólicos"):
            self.build()

    def test_pending_source_selection_and_results_directory_are_rejected(self):
        initialize_project(self.root)
        with self.assertRaisesRegex(ValueError, "no seleccionada"):
            self.build()
        result = self.material("docente/resultados/entregas/informe.md", "Entrega sintética", "docente")
        # Updating configuration deliberately still cannot override permanent exclusions.
        initialize_project(self.root, include=["alumnado", "docente/fuentes"])
        path, metadata = self.metadata("historia")
        metadata["materials"]["entrega"] = result
        self.save(path, metadata)
        with self.assertRaisesRegex(ValueError, "excluida"):
            self.build()

    def test_bad_reference_visibility_or_undeclared_path_is_rejected(self):
        path, metadata = self.metadata("historia")
        for ref in [
            {"title": "Solución", "path": self.materials["examen"]["path"], "access": "estudiante"},
            {"title": "Inventado", "path": "alumnado/materiales/desconocido.md", "access": "estudiante"},
        ]:
            metadata["concepts"]["evidencia"]["references"] = [ref]
            self.save(path, metadata)
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                validate_catalog(self.catalog)

    def test_question_recommendations_cannot_relabel_reserved_materials(self):
        path, metadata = self.metadata("historia")
        metadata["materials"]["examen"] = self.material(
            "archivo/reservado.md", "Soluciones reservadas", "docente")
        for reference in (
            {"title": "Soluciones", "path": "archivo/reservado.md", "access": "estudiante"},
            {"title": "Desconocido", "path": "archivo/sin-declarar.md", "access": "estudiante"},
        ):
            metadata["questions"]["repetida"]["references"] = [reference]
            self.save(path, metadata)
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                validate_catalog(self.catalog)
            self.assertFalse((self.root / "out").exists())

    def test_question_recommendations_accept_declared_student_materials(self):
        path, metadata = self.metadata("historia")
        references = [{"title": "Texto para repasar", "path": self.materials["texto"]["path"],
                       "access": "estudiante"}]
        metadata["questions"]["repetida"]["references"] = references
        self.save(path, metadata)
        self.assertEqual(validate_catalog(self.catalog)["status"], "ok")
        manifest = self.build()
        self.assertEqual(manifest["metadata"]["questions"]["historia::repetida"]["references"], references)

    def test_required_question_metadata_and_full_coverage(self):
        path, original = self.metadata("historia")
        for field in ("source_refs", "concepts", "objective", "difficulty", "guidance"):
            metadata = copy.deepcopy(original)
            del metadata["questions"]["repetida"][field]
            self.save(path, metadata)
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_catalog(self.catalog)
        metadata = copy.deepcopy(original)
        del metadata["questions"]["repetida"]
        self.save(path, metadata)
        with self.assertRaisesRegex(ValueError, "Cada pregunta"):
            validate_catalog(self.catalog)

    def test_catalog_duplicates_and_paths_outside_root_are_rejected(self):
        original = copy.deepcopy(self.catalog_data)
        for addition in [
            copy.deepcopy(original["banks"][0]),
            {**original["banks"][0], "id": "otro"},
            {"id": "escape", "gift": "../escape.gift", "metadata": "historia.json"},
        ]:
            self.catalog_data = copy.deepcopy(original)
            self.catalog_data["banks"].append(addition)
            self.save(self.catalog, self.catalog_data)
            with self.subTest(addition=addition), self.assertRaises(ValueError):
                validate_catalog(self.catalog)

    def test_only_explicitly_selected_banks_are_read(self):
        (self.root / "ciencias.gift").unlink()
        self.select([{"label": "Historia", "count": 2}], banks=["historia"])
        manifest = self.build()
        self.assertEqual([bank["id"] for bank in manifest["source_banks"]], ["historia"])
        with self.assertRaisesRegex(ValueError, "ciencias"):
            validate_catalog(self.catalog)

    def test_relative_paths_resolve_at_catalog_and_course_root(self):
        directory = self.root / "docente/evaluaciones/bancos"
        directory.mkdir(parents=True)
        for path in self.root.glob("*.gift"):
            path.rename(directory / path.name)
        for path in [self.root / "historia.json", self.root / "ciencias.json", self.catalog]:
            path.rename(directory / path.name)
        self.catalog = directory / self.catalog.name
        initialize_project(self.root, include=["alumnado", "docente/fuentes"])
        self.assertEqual(validate_catalog(self.catalog)["questions"], 4)
        self.assertEqual(validate_catalog(self.catalog, project_root=self.root)["questions"], 4)

    def test_contradictory_global_material_and_concept_ids_are_diagnosed(self):
        path, metadata = self.metadata("ciencias")
        metadata["concepts"]["evidencia"]["label"] = "Otro significado"
        self.save(path, metadata)
        with self.assertRaisesRegex(ValueError, "contradictorias"):
            validate_catalog(self.catalog)

    def test_catalog_and_single_bank_flags_cannot_be_mixed(self):
        for options in ({"metadata_path": self.root / "historia.json"},
                        {"per_category": {"ciencias": 2}},
                        {"selection_path": None}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.build(**options)

    def test_empty_bank_and_wrong_metadata_types_are_clear_errors(self):
        path, original = self.metadata("historia")
        for field, invalid in (("difficulty", []), ("source_refs", [{"material_id": [], "locators": ["p1"]}]),
                               ("concepts", "evidencia"), ("objective", False)):
            metadata = copy.deepcopy(original)
            metadata["questions"]["repetida"][field] = invalid
            self.save(path, metadata)
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_catalog(self.catalog)
        self.save(path, original)
        (self.root / "historia.gift").write_text("")
        with self.assertRaisesRegex(ValueError, "vacío"):
            validate_catalog(self.catalog)

    def test_combined_snapshot_is_compatible_with_existing_feedback(self):
        from docencia.feedback import build_feedback

        self.build(models=1)
        config = self.root / "moodle.json"
        self.save(config, {
            "schema_version": 1, "identifier_column": "ID", "model_column": "Modelo",
            "feedback_column": "Comentario", "status_column": "Estado",
            "absent_values": ["No presentado"], "blank_values": [],
            "question_columns": {"1": "P1", "2": "P2"}, "max_scores": {"1": 1, "2": 1},
        })
        results = self.root / "resultados.csv"
        results.write_text("ID;Modelo;Comentario;Estado;P1;P2;Nota final\n"
                           "sintetico-001;A;;Finalizado;0;0;3,5\n", encoding="utf-8")
        # Only the frozen bank is needed after generating the exam.
        (self.root / "historia.gift").unlink()
        (self.root / "ciencias.gift").unlink()
        report = build_feedback(self.root / "out/manifest.json", [results], config,
                                self.root / "feedback")
        self.assertEqual(report["status"], "ok", report)
        with Path(report["outputs"][0]).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        self.assertEqual(rows[0]["Nota final"], "3,5")
        self.assertIn("Medición", rows[0]["Comentario"])
        self.assertIn("Interpretar evidencias", rows[0]["Comentario"])
        self.assertNotIn("1.23456789012345", rows[0]["Comentario"])

    def test_matching_remains_in_snapshot_but_not_in_exam(self):
        self.add_bank("pares", "::parejas::Relaciona.{=A->Uno=B->Dos=C->Tres}")
        self.select([{"label": "Todas las compatibles", "count": 4}])
        manifest = self.build(questions=4, models=1)
        self.assertEqual(manifest["excluded_question_ids"], ["pares::parejas"])
        self.assertNotIn("matching", {q["type"] for q in manifest["models"][0]["questions"]})
        parsed = parse_gift((self.root / "out/source/bank.gift").read_text())
        self.assertIn("matching", {q["type"] for q in parsed})


class SerializationTests(unittest.TestCase):
    def test_full_supported_semantics_and_precise_numbers_roundtrip(self):
        text = (
            "::libre::[plain]Sin categoría{T}\n"
            "$CATEGORY: Ciencia/ñ\n"
            "::peso\\:\\:q::[markdown]Explica \\{x\\} y \\\\(x\\\\). "
            "{=Correcta#Bien~%0.0000001%Parcial#Revisa~Incorrecta####General}\n"
            "::multiple::[plain]Elige.{~%33.33333%A~%33.33333%B~%33.33334%C~%-100%D}\n"
            "::tf::[plain]Afirmación.{FALSE#Fallo#Acierto####General}\n"
            "::numero::[plain]Valor.{#=1.23456789012345:0.00000000012345#Unidades"
            "=%50%1.23456788000001..1.23456789999999####General}\n"
            "::pares::[moodle]Relaciona.{=A->Uno=B->Dos=C->Tres####General}\n"
        )
        first = parse_gift(text)
        self.assertEqual(parse_gift(serialize_bank(first).decode()), first)

    def test_uncategorized_questions_from_multiple_banks_keep_empty_category(self):
        categorized = parse_gift("$CATEGORY: Historia\n::h::Caso.{T}")
        uncategorized = parse_gift("::u::Otro.{F}")
        parsed = parse_gift(serialize_bank(categorized + uncategorized).decode())
        self.assertEqual({q["id"]: q["category"] for q in parsed}, {"h": "Historia", "u": ""})

    def test_empty_feedback_and_truefalse_option_feedback_roundtrip(self):
        for text in ("::x::Caso.{TRUE#}", "::x::Caso.{FALSE##}", "::x::Caso.{T####}"):
            parsed = parse_gift(text)
            self.assertEqual(parse_gift(serialize_bank(parsed).decode()), parsed)


if __name__ == "__main__":
    unittest.main()
