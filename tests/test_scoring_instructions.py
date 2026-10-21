import unittest
from docencia.cuestionarios import render_model

class ScoringInstructionsTests(unittest.TestCase):
    def test_mixed_types_and_actual_weights(self):
        model = {'id': 'A', 'questions': [
            {'number': 1, 'type': 'single', 'prompt': 'Única', 'format': 'plain',
             'options': [{'label': 'A', 'text': 'Uno', 'weight': 100}, {'label': 'B', 'text': 'Dos', 'weight': -50}]},
            {'number': 2, 'type': 'multiple', 'prompt': 'Varias', 'format': 'plain',
             'options': [{'label': 'A', 'text': 'Uno', 'weight': 50}, {'label': 'B', 'text': 'Dos', 'weight': 50}, {'label': 'C', 'text': 'Tres', 'weight': -100}]},
            {'number': 3, 'type': 'numerical', 'prompt': 'Valor', 'format': 'plain',
             'numerical': [{'value': 123456, 'tolerance': 1, 'weight': 100}]}
        ]}
        result = render_model(model, 'Prueba', teacher=False)
        self.assertIn('questionnaire-header', result)
        self.assertIn('Marque una sola opción', result)
        self.assertIn('Marque las opciones que correspondan', result)
        self.assertIn('por error: -0.5', result)
        self.assertIn('por acierto: 0.5', result)
        self.assertIn('Escriba un valor numérico', result)
        self.assertNotIn('123456', result)
        self.assertNotIn("class='answer'", result)
        self.assertIn("options square", result)
        self.assertIn("options circle", result)
        self.assertIn("VARIAS RESPUESTAS", result)
        self.assertIn("identity-grid", result)
        self.assertNotIn("Moodle estándar", result)
        self.assertNotIn("confirme con el docente", result)
