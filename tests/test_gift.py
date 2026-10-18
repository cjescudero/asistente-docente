"""Behavior tests of the supported GIFT subset and refusal of lossy inputs."""

import json
import unittest

from docencia.gift import GiftError, escape_gift, parse_gift


class GiftParserTests(unittest.TestCase):
    def question(self, body, prompt="¿Qué opción?", name="Q-ñ"):
        return parse_gift(f"::{name}::{prompt}{{{body}}}")[0]

    def test_unicode_categories_ids_and_option_order(self):
        questions = parse_gift(
            "\ufeff// Un comentario con {llaves} y ::títulos::\r\n"
            "$CATEGORY: $course$/top/Literatura/Épica\r\n\r\n"
            "::épica-1::[html]<p>¿Quién escribió <em>La Odisea</em>?</p>{"
            "~Virgilio#Obra diferente. =Homero#¡Correcto! ~Ovidio}"
            "\n\n$CATEGORY: Historia/Antigüedad\n"
            "::historia-2::Una afirmación.{FALSE}\n"
        )
        first, second = questions
        self.assertEqual(first["id"], "épica-1")
        self.assertEqual(first["category"], "$course$/top/Literatura/Épica")
        self.assertEqual(first["type"], "single")
        self.assertEqual(first["format"], "html")
        self.assertEqual([o["text"] for o in first["options"]], ["Virgilio", "Homero", "Ovidio"])
        self.assertEqual([o["weight"] for o in first["options"]], [0, 100, 0])
        self.assertEqual(first["options"][0]["feedback"], "Obra diferente.")
        self.assertEqual(second["category"], "Historia/Antigüedad")
        self.assertFalse(second["true_answer"])
        json.dumps(questions, ensure_ascii=False, allow_nan=False)

    def test_question_formats_and_default(self):
        for fmt in ("html", "plain", "markdown", "moodle"):
            with self.subTest(format=fmt):
                result = self.question("=Sí~No", prompt=f"[{fmt}]¿Válido?")
                self.assertEqual(result["format"], fmt)
                self.assertEqual(result["prompt"], "¿Válido?")
        result = self.question("=Sí~No")
        self.assertEqual(result["format"], "moodle")
        self.assertEqual(result["category"], "")

    def test_multiline_questions_and_comments_do_not_damage_urls(self):
        result = parse_gift(
            "  // comentario\n::uno::[markdown]Primera línea\n"
            "Segunda: https://example.org/a//b\n{\n"
            "// comentario dentro de respuestas\n~No\n=Sí\n}\n"
        )[0]
        self.assertEqual(result["prompt"], "Primera línea\nSegunda: https://example.org/a//b")
        self.assertEqual(result["options"][1]["text"], "Sí")

    def test_escaped_special_characters_and_literal_backslash(self):
        literal = "¿A = B? {x} ~ # : \\alpha \\nu\n¡Sí, ñ!"
        escaped = escape_gift(literal)
        result = parse_gift(f"::q\\:1::{escaped}{{={escaped}~Otra}}")
        self.assertEqual(result[0]["id"], "q:1")
        self.assertEqual(result[0]["prompt"], literal)
        self.assertEqual(result[0]["options"][0]["text"], literal)
        self.assertNotIn("\n", escaped)

    def test_tex_with_escaped_braces_is_content(self):
        formula = r"\\frac\{a\}\{b\} \= 2"
        result = self.question("=Correcta~Incorrecta", prompt=formula)
        self.assertEqual(result["prompt"], r"\frac{a}{b} = 2")

    def test_unknown_backslash_escape_preserved(self):
        result = self.question("=Bien~Mal", prompt=r"Valor de \alpha y \pi")
        self.assertEqual(result["prompt"], r"Valor de \alpha y \pi")

    def test_backslash_parity_does_not_hide_structural_delimiter(self):
        result = self.question(r"=ruta\\~otra")
        self.assertEqual([o["text"] for o in result["options"]], ["ruta\\", "otra"])

    def test_feedback_general_and_per_option_with_escapes(self):
        result = self.question(r"~No#Revisa \#1.=Sí#A \= B.####Relación \{A\}.")
        self.assertEqual(result["options"][0]["feedback"], "Revisa #1.")
        self.assertEqual(result["options"][1]["feedback"], "A = B.")
        self.assertEqual(result["feedback"], "Relación {A}.")

    def test_single_choice_partial_credit_is_not_multiple(self):
        result = self.question("~%25%Parcial~%-50%Errónea=Completa")
        self.assertEqual(result["type"], "single")
        self.assertEqual([o["weight"] for o in result["options"]], [25, -50, 100])

    def test_multiple_choice_preserves_positive_and_negative_weights(self):
        result = self.question("~%-100%Ninguna~%50%Primera~%50%Segunda~Otra")
        self.assertEqual(result["type"], "multiple")
        self.assertEqual([o["weight"] for o in result["options"]], [-100, 50, 50, 0])

    def test_thirds_precision(self):
        result = self.question("~%33.33333%A~%33.33333%B~%33.33333%C~%-100%D")
        self.assertEqual(result["type"], "multiple")
        self.assertEqual(result["options"][0]["weight"], 33.33333)

    def test_truefalse_short_long_and_feedback_correctness(self):
        for token, expected in (("T", True), ("TRUE", True), ("F", False), ("FALSE", False)):
            with self.subTest(token=token):
                result = self.question(token)
                self.assertIs(result["true_answer"], expected)
                self.assertEqual(result["type"], "truefalse")
        result = self.question("FALSE#Incorrecto#Correcto####Concepto general")
        self.assertEqual(result["options"][0], {"text": "Verdadero", "weight": 0, "feedback": "Incorrecto"})
        self.assertEqual(result["options"][1], {"text": "Falso", "weight": 100, "feedback": "Correcto"})
        self.assertEqual(result["feedback"], "Concepto general")

    def test_truefalse_one_feedback_applies_to_wrong_answer(self):
        result = self.question("T#Revisa la afirmación")
        self.assertEqual(result["options"][0]["feedback"], "")
        self.assertEqual(result["options"][1]["feedback"], "Revisa la afirmación")

    def test_numeric_compact_tolerance_and_scientific_notation(self):
        result = self.question("#-1.25e2:2.5#Unidades correctas")
        self.assertEqual(result["type"], "numerical")
        self.assertEqual(result["numerical"], [{"value": -125, "tolerance": 2.5, "weight": 100, "feedback": "Unidades correctas"}])
        self.assertEqual(self.question("#.5")["numerical"][0]["tolerance"], 0)

    def test_numeric_interval(self):
        result = self.question("#-2.5..+3e1")
        self.assertEqual(result["numerical"], [{"min": -2.5, "max": 30, "weight": 100, "feedback": ""}])

    def test_multiple_weighted_numeric_answers_preserve_order(self):
        result = self.question("#\n=1822:0#Exacto\n=%50%1820..1824#Cerca\n####Recuerda el contexto")
        self.assertEqual(result["numerical"][0]["value"], 1822)
        self.assertEqual(result["numerical"][0]["weight"], 100)
        self.assertEqual(result["numerical"][1], {"min": 1820, "max": 1824, "weight": 50, "feedback": "Cerca"})
        self.assertEqual(result["feedback"], "Recuerda el contexto")

    def test_matching_unicode(self):
        result = self.question("=España->Madrid=Italia->Roma=Japón->Tokio####Capitales")
        self.assertEqual(result["type"], "matching")
        self.assertEqual(result["matches"], [
            {"left": "España", "right": "Madrid"},
            {"left": "Italia", "right": "Roma"},
            {"left": "Japón", "right": "Tokio"},
        ])

    def test_adjacent_compact_questions_keep_distinct_ids(self):
        result = parse_gift("::1::¿Una?{T}\n::2::¿Dos?{F}")
        self.assertEqual([q["id"] for q in result], ["1", "2"])

    def test_empty_comment_only_bank(self):
        self.assertEqual(parse_gift("\n// comentario\n"), [])

    def test_rejects_unnamed_empty_duplicate_ids(self):
        cases = ["¿Pregunta?{T}", "::::¿Pregunta?{T}", "::id::A{T}\n::id::B{F}",
                 "::q\\:1::A{T}\n::q:1::B{F}", "::primera\nlínea::A{T}"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(GiftError):
                parse_gift(text)

    def test_rejects_unsupported_question_types(self):
        bodies = ["", "=palabra", "=palabra=sinónimo", "respuesta corta", ":MULTICHOICE:=A~B"]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(GiftError):
                self.question(body)

    def test_rejects_unescaped_tex_braces_nested_cloze_and_extra_blocks(self):
        cases = [
            r"::x::Calcula \frac{a}{b}.{=A~B}",
            r"::x::Explica \text{=sí~no}",
            "::x::Calcula x^{=a~b}",
            "::x::Contenido {anidado {otro}}{=A~B}",
            "::x::Uno {=A~B} y dos {=C~D}",
            "::x::Falta } escapar{=A~B}",
            "::x::Cloze {1:MULTICHOICE:=A~B}",
        ]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(GiftError):
                parse_gift(text)

    def test_rejects_trailing_missing_word_text_and_truncated_blocks(self):
        cases = ["::x::Dos más {=dos~tres} son cuatro.", "::x::Pregunta{=A~B", "::x::Pregunta", "::x::Pregunta\n::y::Otra{T}"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(GiftError):
                parse_gift(text)

    def test_rejects_ambiguous_choice_or_malformed_weights(self):
        cases = ["=A=B~C", "=A~A", "=A~", "~A~B", "~%30%A~%30%B", "~%60%A~%60%B",
                 "=A~%101%B", "=A~%-101%B", "=A~%NaN%B", "=A~%50B", "=%50%A~B",
                 "=A~%100%B", "=A#Uno#Dos~B", "=A~B####Uno####Dos"]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(GiftError):
                self.question(body)

    def test_rejects_invalid_numerical_input(self):
        cases = ["#", "#NaN", "#inf", "#1e999", "#1:-0.1", "#2..1", "#1:2:3", "#1,5",
                 "#1..2:1", "#=1~2", "#1=2", "#%50%2", "#=%50%2", "#1e308:1e308"]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(GiftError):
                self.question(body)

    def test_rejects_invalid_matching(self):
        cases = ["=a->A=b->B", "=a->A=b->B=c", "=a->A=a->B=c->C", "=a->A=b->B=->C",
                 "=%50%a->A=b->B=c->C", "=a->A#Comentario=b->B=c->C"]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(GiftError):
                self.question(body)

    def test_rejects_invalid_format_empty_prompt_and_category(self):
        cases = ["::x::[latex]Q{T}", "::x::{T}", "$CATEGORY: \n::x::Q{T}", "::x::Q{=[html]A~B}"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(GiftError):
                parse_gift(text)

    def test_errors_identify_the_question(self):
        with self.assertRaisesRegex(GiftError, "pregunta-73"):
            parse_gift("::pregunta-73::¿Valor?{#NaN}")

    def test_truefalse_cannot_discard_extra_feedback(self):
        with self.assertRaises(GiftError):
            self.question("T#Uno#Dos#Tres")

    def test_argument_types(self):
        with self.assertRaises(TypeError):
            parse_gift(None)
        with self.assertRaises(TypeError):
            escape_gift(42)


if __name__ == "__main__":
    unittest.main()
