"""Smoke-test the runnable course shipped in both distributions."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BilingualWorkflowTests(unittest.TestCase):
    def test_mixed_course_from_outside_installation(self):
        runner = Path(__file__).resolve().parents[1] / "examples/bilingual-course/run.py"
        with tempfile.TemporaryDirectory() as temp:
            course = Path(temp) / "Course"
            result = subprocess.run([sys.executable, str(runner), str(course)], cwd=temp,
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((course / "AI-generated materials/Course map/index.html").is_file())
