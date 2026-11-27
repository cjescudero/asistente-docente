# Asistente docente / Teaching Assistant

English · [Español](README.md)

Turn course materials into a linked course wiki, assignments, study notes, printable quizzes and individual Moodle feedback. Bring your existing course folder. You choose the sources, the language of the materials and which files students receive.

**Adapting the assistant for a study?** The [researcher guide](docs/RESEARCHER-GUIDE.md) maps all twelve skills to their source files and shows how to test a change on a synthetic course.

## Install and start

1. **Install in your teaching environment.** Choose your route from the table below. The GitHub marketplace address is `https://github.com/cjescudero/asistente-docente`. The plugin identifier is `asistente-docente`.
2. **Open your course folder** and give the agent access. A locally available OneDrive or SharePoint folder also works. If your host does not automatically read project instructions, ask it to read the course's `AGENTS.md`.
3. Say **“Set up my course.”** For a new English course the agent proposes **Course materials**, **AI-generated materials** and **Student submissions**. You can assign your existing folders and keep the original files in place. Choose which sources the course map may use. Ask **“What can I do next?”** at any point.

| Environment | How to install |
| --- | --- |
| ChatGPT in a managed workspace | Give the repository address to your workspace administrator. In the admin console they open **Plugins → Add → Import marketplace**, enter the repository address, leave the path empty, import it and enable the plugin. You can then install Teaching Assistant from your **workspace plugins**. Individual users can use the Codex route below. |
| Claude Cowork | Open **Cowork → Customize → Plugins → Add → Add marketplace → Add from a repository**. Enter the repository address. In **Discover**, select the plugin from that marketplace and click **Add**. Your organization may need to allow the repository. |
| Codex | Run `codex plugin marketplace add https://github.com/cjescudero/asistente-docente.git`. In Codex, open `/plugins`, select the marketplace and install the plugin. Start a new session in your course folder. |
| Claude Code | In Claude Code, run `/plugin marketplace add cjescudero/asistente-docente` and then `/plugin install asistente-docente@asistente-docente`. Start a new session in the course folder. |
| OpenCode 2.x | Download the full source archive or clone the repository outside your course. Add the absolute path to its `skills/` directory to your course's `opencode.json`. Use `{"skills":["/path/to/asistente-docente/skills"]}`. Merge with any existing settings and restart OpenCode. |

[GitHub source and downloads](https://github.com/cjescudero/asistente-docente/releases) · [Workspace marketplace administration](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github) · [Claude plugins](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) · [OpenCode skills](https://opencode.ai/docs/skills/)

## Your first course

Try the [bilingual sample course](examples/bilingual-course/README.md). An English-speaking teacher uses a Spanish source about measurement to design a practical activity and a quiz.

| Ask the agent | What to expect |
| --- | --- |
| “Build my course map in English.” | Linked explanatory pages, source references, an offline HTML reader and a concept graph. Ask “What does the map say about measurement?” to consult it. |
| “Design a measurement activity and a rubric.” | A dialogue about outcomes, evidence and resources, followed by a student brief and templates. The detailed rubric and marking guide are for the teacher. |
| “Grade these submissions using the rubric.” | Evidence-based feedback and a copy of your Moodle grading CSV with the approved grades and comments. Supply the downloaded submissions, the original worksheet and its identification columns. |
| “Create a question bank from this unit.” | Questions linked to the source, with variants, suggested coverage and an editable GIFT bank. |
| “Prepare four printable quiz forms.” | Student forms, separate answer keys, masked Moodle GIFT files and a frozen manifest. Review and print the PDFs. Import the GIFT categories into Moodle, select the corresponding form and disable question and answer shuffling. |
| “Give my students feedback on this quiz.” | Supply the frozen manifest, Moodle's question-level results and the target gradebook/profile. Review the feedback CSV and import it manually. The existing quiz grades are preserved. |
| “Prepare study notes” or “Create a visual slide.” | Source-based notes or a single educational visual. If image generation is unavailable, the agent provides the design and prompt. |

You can say **“Speak to me in English and write the student handout in Spanish.”** Set a course-wide preference or change it for one task. The original source language, filenames and Moodle column headings are preserved. Plain Spanish is an optional writing style you can request for Spanish documents.

PDF export uses Python, Playwright and Chromium. For assistance, ask **“Check whether I can generate PDFs on this computer.”** If PDF generation is unavailable, you can review the editable source and HTML. Folder names describe the intended audience. Check actual file-sharing permissions before distributing student materials.
