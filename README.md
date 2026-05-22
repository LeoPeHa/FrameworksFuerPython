# FrameworksFuerPython

Projekt für die Abschlussübung des Wahlpflichtfachs "Frameworks für Python" im SS26.

## Zielsetzung

Erstelle einen Server mit FastAPI, der CRUD-Operationen implementiert, mit dem Tasks erstellt werden können, mit anderen Tasks verknüpft werden können, Listen zugewiesen werden können und als offen oder abgeschlossen markiert werden können.

## Initialprompt
Use FastAPI, Python with uv. I want to create a CRUD Server. The CRUD Server should be able to handle Tasks. Each Task has a title, a description and a status. The status can be 'open' or 'closed'. Tasks can be linked to other Tasks. Tasks can be assigned to Lists. All data should be stored in a database, use SQLite. Implement all CRUD operations for Tasks and Lists. Also implement the functionality to link Tasks and to assign Tasks to Lists.

The following requests should be implemented:
- GET /tasks
- GET /tasks/{id}
- POST /tasks
- PUT /tasks/{id}
- DELETE /tasks/{id}
- GET /lists
- GET /lists/{id}
- POST /lists
- PUT /lists/{id}
- DELETE /lists/{id}
- POST /tasks/{id}/link/{other_id}
- POST /tasks/{id}/assign/{list_id}

## Log
- 12:03: Server läuft, reagiert auf Anfrage, werde jetzt manuell nachtesten. Weitere Ziele: API-Key, vielleicht noch eine CLI-App oder etwas mit Flutter, je nachdem wie es funktioniert. Weitere Ideen: Tasks klar als Voraussetzung, Unterscheidung in optional/verpflichtend, Anzeige von Folgetasks, Zieldatum, Priorität.

- 12:29: Listen- und Taskoperationen funktionieren. Idee: minimale GUI. Eine andere hatte ich eben auch, aber schon wieder vergessen.

- 12:35: Fehlende Funktionen: Tasks trennen, von Liste streichen. Auch Überlegung: Muss der komplette Task als related Task zurückgegeben werden oder reicht die ID? Genau das gleiche bei den Listen. Andererseits muss dann auch wieder ein Folgerequest kommen für den Rest der Tasks. Lassen wir es mal so.

- 12:38: Zwischenfazit: Das läuft echt gut, ich sollte das mal in PHP umsetzen damit es auf Wald- und Wiesenhostern läuft, muss aber wegen HTTPS gucken.

- 12:42: Ich könnte das Frontend über Web mithilfe von Jinja2 umsetzen.

- 13:13: Verknüpfung und Listenzuordnungen trennbar, muss noch nachtesten.

- 13:30: Nachtesten erfolgreich, Feedback des Dozenten: Keine weitere Sprache, Flutter damit raus, keine explizite Äußerung zu API-Key, mache ich also, alles andere fühlt sich komisch an, CLI oder GUI überlege ich noch, beides wäre schon nice, aber CLI ist universeller und bei der GUI muss ich überlegen, wie das auf Windows/MacOS funktioniert, gerade könnte ich nur Windows zusätzlich testen. Die Architektur und den Code finde ich soweit überschaubar, aber ich gehe da nochmal drüber, mal gucken was Antigravity so für Linter bietet.

- 13:38: Wenig überraschend hat Antigravity im Vergleich mit VS Code eine deutlich geringere Pluginauswahl, die Vervollständigungsvorschläge finde ich auch unnötig lange, die LLM-Unterstützung für Boilerplate ist jedoch angenehm umfangreich und wäre überlegenswert für private Projekte. Mal testen ob hier Unterpunkte funktionierne.
    - Punkt 1
    - Punkt 2
    - Punkt 3