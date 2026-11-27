# Adapting Teaching Assistant for a research study

Suppose you want to study whether asking learners to predict an outcome helps them interpret a measurement. The assistant can prepare the activity, the wording of the prompt and the scoring rubric. If a separate tutor delivers hints to participants, implement and test the timing of those hints in that tutor as well. Generating an activity sheet only establishes what appears on the sheet.

## Find the procedure you want to change

Work in a clone or fork of the repository. Each link in the first column opens the actual file to edit. Its opening `description` helps the host select the skill. The Markdown below it tells the agent how to carry out the task. References beside a skill contain more detailed rules. The neighbouring `agents/openai.yaml` controls its presentation in OpenAI hosts.

| Skill source | What you can change there | Where related behaviour lives |
| --- | --- | --- |
| [Course setup and adaptation](../skills/proyecto-docente-inicializacion-adaptacion/SKILL.md) | Which questions the teacher is asked about sources, languages and folders. | [Course spaces](../docencia/spaces.py) implements folder choices and generated project instructions. |
| [Inline course help](../skills/proyecto-docente-ayuda/SKILL.md) | How the agent uses course state and prior decisions to suggest the next step. | The skill also defines when to return to the task that triggered the question. |
| [Build and display the course map](../skills/mapa-docente-creacion-visualizacion/SKILL.md) | How much explanation to include, how to cite the original and how to separate restricted pages. | [English page templates](../templates/mapa-docente/en/index.md), [HTML reader](../scripts/build_wiki.py) and [graph generator](../scripts/build_graph.py). |
| [Consult the course map](../skills/mapa-docente-consulta/SKILL.md) | How to follow the index to a claim, verify it in the source and report insufficient evidence. | Use a read-only question to test retrieval independently of map creation. |
| [Design activities](../skills/actividades-preparacion/SKILL.md) | What learners are asked to do and what evidence they must submit. | [Design dialogue](../skills/actividades-preparacion/references/actividades.md), [student brief](../templates/en/activity-brief.md) and [teacher rubric](../templates/en/marking-rubric.md). |
| [Grade activities](../skills/actividades-evaluacion/SKILL.md) | How to apply a rubric, justify marks and word feedback on student submissions. | [Assessment rules](../skills/actividades-evaluacion/references/evaluacion.md) and [Moodle grade export](../docencia/grading.py). |
| [Create question banks](../skills/cuestionarios-bancos-preguntas-creacion/SKILL.md) | Coverage, difficulty, variants and guidance for reviewing a concept. | [GIFT guidance](../skills/cuestionarios-bancos-preguntas-creacion/references/gift.md) and [bank validation](../docencia/banks.py). |
| [Build printable quizzes](../skills/cuestionarios-modelos-imprimir-evaluar/SKILL.md) | How to agree on the quiz length, topics and number of forms. | [Quiz generator](../docencia/cuestionarios.py) controls print order, answer keys and masked Moodle labels. |
| [Give feedback on quiz scores](../skills/cuestionarios-observaciones-calificaciones-alumnado/SKILL.md) | What to explain from question-level evidence and when to discuss selected options. | [Feedback generator](../docencia/feedback.py) implements concept prioritisation and writes comments to a copy of the Moodle CSV. |
| [Write study notes](../skills/apuntes-estudio-creacion/SKILL.md) | Level, explanation, worked examples and references to course sources. | Test by comparing the resulting notes with a specific passage of the source. |
| [Create a teaching visual](../skills/infografias-didacticas-creacion/SKILL.md) | Which concept a single visual should convey and how to adapt it to the audience. | [Composition](../skills/infografias-didacticas-creacion/references/composicion.md) and [image prompt](../skills/infografias-didacticas-creacion/references/prompt.md). |
| [Write in plain Spanish](../skills/espanol-conciso-redaccion/SKILL.md) | The optional style used when a teacher requests plain Spanish. | For academic English in one study, put the agreed style in the course instructions or the activity request. The [language guide](LANGUAGES.md) explains how to set the output language. |

You can edit the shared instructions in English. If you translate an existing rule, preserve its conditions and exceptions and replace the passage in place so the agent sees one procedure. Keep skill identifiers, file links, record keys, Moodle headers and question IDs intact. For example, translating a comment for a learner should never change the identifier used to join it to a grade.

## Try one change with an agent

1. **Record the baseline.** Run `git rev-parse HEAD` in your clone. In a fresh course folder, place a copy of [Mediciones.md](../examples/bilingual-course/Mediciones.md) under `Course materials/`. Start a new agent session using the local clone. In Claude Code, for example, run `claude --plugin-dir "/absolute/path/to/asistente-docente"` from the course folder. Check that the loaded activity skill comes from that clone, especially if you also have a marketplace installation.
2. **Give the baseline task.** Say *“Set up my course in English. Use Course materials as the source. Design a 20-minute activity based on Mediciones.md for first-year students working in pairs. They have a scale and a reference mass. Produce a student worksheet and a separate four-point teacher rubric.”* Answer any design questions and save the worksheet, rubric and conversation.
3. **Change one instruction.** In the activity-design skill, under the instructions for producing the student brief, add: *“For this measurement workshop, put a prediction box before the first reading. Ask learners to predict whether averaging more readings will remove a fixed offset and justify their prediction in one sentence. Reserve the explanation for the teacher’s guide.”* Keep this study-specific change on your research branch.
4. **Repeat with the edited clone.** Open a new session in a second fresh course folder with the same source, initial prompt, model settings and answers to follow-up questions. Ask the host to show which skill file it used. An installation pointing to the released copy will still produce baseline behaviour.
5. **Score both outputs using the same checks.** Is there a prediction box before the first reading? Does it ask for a reason? Does the worksheet disclose the explanation? Does the separate rubric still total four points? A baseline may already meet some criteria. Record what you observe. Keep the commit, host, model, prompts and outputs with each condition so another investigator can repeat the comparison.

## Check generated files with the runnable course

The [bilingual example](../examples/bilingual-course/README.md) exercises the file utilities with fixed synthetic inputs. Run these commands at the root of your clone using Python 3.10 or later in an activated virtual environment. Choose a new destination outside the clone for each run.

```sh
python -m pip install -r requirements-dev.txt
python examples/bilingual-course/run.py ../measurement-course-check
python -m unittest discover -s tests -p "test_bilingual_workflow.py" -v
python scripts/validate_plugin.py --public
```

Open `AI-generated materials/Course map/index.html` in the generated course and follow the measurement topic to its Spanish source. Under `Scale workshop` in the generated materials, inspect the student brief and the separate teacher rubric. Under `Measurement quiz`, compare the printable form, masked GIFT and frozen manifest. Under `Student submissions/Measurement quiz/`, compare the English and Spanish feedback CSVs against the synthetic Moodle input. Student IDs, grade values and column headings should match.

The runner copies prepared activity text and calls the utilities directly. A passing run verifies file generation and data handling. To verify an edit to a teaching instruction, use the live comparison above. For a Python change, also run the relevant unit tests, for example `python -m unittest discover -s tests -p "test_feedback.py" -v` for feedback, then the full suite with `python -m unittest discover -s tests -v`.
