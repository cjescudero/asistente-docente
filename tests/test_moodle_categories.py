import tempfile
import unittest
from pathlib import Path
from docencia.cuestionarios import build_cuestionarios
from docencia.gift import parse_gift

class MoodleCategoriesTests(unittest.TestCase):
    def test_categories_and_visible_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bank = root / 'banco.gift'
            bank.write_text('::01-A::Texto privado{=Bien ~%-50%Mal}', encoding='utf-8')
            output = root / 'salida'
            build_cuestionarios(bank, output, title='Talleres 5-8', questions=1, models=2, html_only=True)
            import json
            manifest = json.loads((output / 'manifest.json').read_text())
            for i, model in enumerate(manifest['models'], 1):
                expected = f'$course$/top/RespuestasCuestionariosOffline/Talleres 5-8/Modelo {i:02d}'
                self.assertEqual(model['moodle_category'], expected)
                text = (output / model['files']['gift']).read_text()
                parsed = parse_gift(text)
                self.assertEqual(parsed[0]['category'], expected)
                self.assertNotIn('Texto privado', text)
                self.assertEqual(sorted(o['weight'] for o in parsed[0]['options']), [-50, 100])
                self.assertIn(f'Modelo {i:02d}', (output / model['files']['student_html']).read_text())
