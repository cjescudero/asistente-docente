# Starting an English course map

Work inside the course's agreed map folder. Copy index.md, LEEME.md, incidencias.md and log.md. In a configured course, place fuentes.json under _datos_internos/. For a standalone map with a registry at its root, adjust the two inventory links accordingly. Retain the registry keys and access values. Use the two page templates only for sources or topics you have actually reviewed.

Set the registry title, fill in the selected source roots relative to the map and link the pages using ordinary Markdown. Keep student and restricted materials separate. Run the map validator, then generate the offline reader and graph using build_graph.py with --wiki-output. Pass --language en for a standalone map. Keep the general reader and teacher graph with the teaching team.
