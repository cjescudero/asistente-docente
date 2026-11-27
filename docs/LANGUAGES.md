# Course and material languages / Idiomas del curso y de los materiales

Respond in the teacher's language. Use the language explicitly requested for the deliverable, then the saved material preference, then the teacher's working language. A one-off request never changes a saved course preference. Save a preference when the teacher establishes it for the course. Spanish remains the standalone default when there is no language context. The supported utility locales are `en` and `es`.

For “Set up my course”, pass the teacher's language to initialization. Reuse configured spaces exactly as saved. Do not translate or rename folders when changing languages. For “Speak English and make a Spanish quiz”, explain the plan in English and pass Spanish to the quiz builder. Continue using the same frozen quiz manifest when the teacher later requests feedback in English. Use the actual Moodle headers and identifiers in the column profile. Keep the teacher's original titles, source quotations and locators, even when explanations change languages.

Read the shared skill procedure in either conversation language. Localize all teacher- and student-facing text you author, including headings, examples, assignment instructions, rubric levels, review suggestions and accessibility text. Use only student-accessible sources in student materials. Retain technical record keys, identifiers, GIFT syntax and input filenames. Describe diagnostic messages to the teacher in their conversation language, preserving the failing path or identifier. Use plain Spanish only on explicit request for Spanish content.

Al trabajar en español se aplican las mismas prioridades. El docente puede pedir una wiki en inglés basada en originales en español, mantener los enunciados en español y recibir las orientaciones en inglés. Para ejemplos de peticiones y del recorrido completo, consulta la [guía inglesa](../README.en.md).

## Utility examples

Use `init-project COURSE --language en --output-language es` for English conversations with Spanish materials. For a single quiz, Markdown document, reader, graph or feedback export, pass `--language en` or `--language es` to the relevant command. A quiz uses the bank's actual questions and options. Author the bank in the target language before printing.

When feedback will be delivered in a second language, add `translations.en` or `translations.es` to the question and concept entries in bank metadata. Translate every student-facing label and guidance field. For optional detailed feedback, key translated `option_feedback` by the zero-based original option index. If the quiz is already frozen, add these translations to the feedback column profile under `translations.concepts` and `translations.questions`, keyed by the frozen IDs. Review the resulting comments for untranslated guidance. Keep original titles, filenames, Moodle headers and score cells verbatim.
