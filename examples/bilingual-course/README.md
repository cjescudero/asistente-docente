# A measurement workshop in two languages

Copy [Mediciones.md](Mediciones.md) into a new course folder, keeping its original title. Give the agent access to the folder and try the requests below. All data in this example are synthetic.

1. **“Set up my course. Speak English, prepare my materials in English, and keep my original file in place.”** Agree the source selection and storage spaces.
2. **“Build my course map from Mediciones.md. Explain in English why taking more readings cannot correct a miscalibrated scale. Cite the source section.”** Check the HTML reader and graph, then open the original from the map.
3. **“Design a short weighing activity. Students can use AI, but must explain one decision with their own readings. Give students a worksheet and prepare a separate teacher rubric.”** The student brief should explain the task and general criteria. Keep the full rubric and solutions with teacher materials.
4. **“Create a question bank covering repeatability and calibration. Show me the proposed coverage. Then prepare the agreed printable quiz forms and Moodle response sheets.”** Check the number and order of questions and options across the student form, answer key and GIFT.
5. **“Give my students feedback in English from their question-level results. My Moodle headers are in Spanish.”** Map the real headers and student identifiers, leave Moodle grades intact and review the output CSV.
6. **“Now create a Spanish quiz from a Spanish-language bank; keep advising me in English.”** Check that the forms, printed instructions and masked GIFT labels agree. Open the original English form again and confirm that it retains its language and correspondence.

Spanish equivalents include **«Inicia mi proyecto docente»**, **«Crea el mapa en inglés»** and **«Prepara cuatro modelos de cuestionario»**.

## Run the file-based example

With the plugin's Python dependencies installed, run `python examples/bilingual-course/run.py /path/to/new-course` from the repository. Choose a destination that does not exist. Add `--pdf` to require actual PDF exports. The script uses the supplied synthetic class materials, builds the English reader and quiz, and writes separate English and Spanish feedback copies of the same Moodle sheet. The conversational requests above let you try the teaching decisions in your own host.
