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