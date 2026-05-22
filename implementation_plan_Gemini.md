# Implementation Plan - FastAPI Tasks and Lists CRUD Server

Create a robust, fully-tested CRUD server using FastAPI, Python (managed by `uv`), and SQLite. The application will handle Tasks and Lists, with advanced support for linking tasks to each other (self-referential symmetric relationship) and assigning tasks to lists.

---

## User Review Required

> [!IMPORTANT]
> The database schema features a **symmetric self-referential relationship** for task linking. This means linking task A to task B will automatically make task B linked to task A, allowing easy bi-directional navigation.
> 
> Deleting a List will set the `list_id` of all associated tasks to `NULL` (`SET NULL` cascade), preserving the tasks themselves.

---

## Proposed Architecture & Database Schema

We will organize the code cleanly using standard FastAPI layout:
- **`database.py`**: Initializes SQLAlchemy engine and SessionLocal.
- **`models.py`**: Defines the SQLAlchemy database models (`Task`, `List`, and `task_links` association table).
- **`schemas.py`**: Defines Pydantic validation schemas.
- **`crud.py`**: Core CRUD operations/business logic.
- **`main.py`**: Configures the FastAPI app, router, endpoints, and middleware.
- **`tests/test_main.py`**: Pytest suite for end-to-end integration testing of all routes and requirements.

### Database Entities

#### 1. `List`
*   `id`: Integer (Primary Key)
*   `name`: String (Required)
*   `description`: String (Optional)
*   `tasks`: Relationship to `Task` (One-to-Many)

#### 2. `Task`
*   `id`: Integer (Primary Key)
*   `title`: String (Required)
*   `description`: String (Optional)
*   `status`: String (Required, restricted to `'open'` or `'closed'`, default: `'open'`)
*   `list_id`: Integer (Foreign Key pointing to `List.id`, nullable, ondelete="SET NULL")
*   `links`: Self-referential relationship via `task_links` table (Many-to-Many, symmetric)

#### 3. `task_links` (Association Table)
*   `task_id`: Integer (Foreign Key pointing to `Task.id`, primary key)
*   `linked_task_id`: Integer (Foreign Key pointing to `Task.id`, primary key)

---

## Proposed Changes

### [NEW] Project & Core Configuration Files

#### [NEW] [pyproject.toml](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/pyproject.toml)
Configures python dependencies using `uv`.
- Dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic`.
- Development Dependencies: `pytest`, `httpx`.

#### [NEW] [database.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/database.py)
Sets up SQLite database connection and local session generator:
- Connects to local `tasks.db` SQLite file.
- Disables same-thread check for SQLite to allow multiple threads.

#### [NEW] [models.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/models.py)
Defines ORM models for SQLite using SQLAlchemy. Contains:
- `List` model.
- `Task` model.
- `task_links` association table.

#### [NEW] [schemas.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/schemas.py)
Defines Pydantic V2 schemas for input validation and output serialization:
- Restricts `status` using Literal or Enum (`'open'`, `'closed'`).
- Handles response nesting to display lists, tasks, and task links without infinite recursion.

#### [NEW] [crud.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/crud.py)
Implements clean data-access logic for Lists and Tasks, separating database operations from route logic:
- Standard CRUD for Lists (create, read all, read one, update, delete).
- Standard CRUD for Tasks (create, read all with filtering, read one, update, delete).
- Linking/Unlinking task functionality (symmetric).
- Assigning task to list.

#### [NEW] [main.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/main.py)
FastAPI application router mapping HTTP requests to CRUD operations:
- **`GET /tasks`**: Retrieve tasks, support optional filtering by `status` or `list_id`.
- **`GET /tasks/{id}`**: Retrieve specific task by ID.
- **`POST /tasks`**: Create new task.
- **`PUT /tasks/{id}`**: Update specific task fields.
- **`DELETE /tasks/{id}`**: Remove a task.
- **`GET /lists`**: Retrieve all lists.
- **`GET /lists/{id}`**: Retrieve specific list details along with its tasks.
- **`POST /lists`**: Create a new list.
- **`PUT /lists/{id}`**: Update list fields.
- **`DELETE /lists/{id}`**: Remove list (sets related tasks' list_id to NULL).
- **`POST /tasks/{id}/link/{other_id}`**: Interlink two tasks symmetrically.
- **`POST /tasks/{id}/assign/{list_id}`**: Assign task to a list.

#### [NEW] [tests/test_main.py](file:///home/leonard/Dropbox/25_Studium/26SS/Frameworks%20f%C3%BCr%20Python/%C3%9Cbung/tests/test_main.py)
Complete automated pytest suite to test:
- CRUD operations for lists.
- CRUD operations for tasks.
- Task status restrictions.
- Linking tasks (verifies bi-directional access and prevents duplicate links).
- Assigning tasks to lists and verifying correct query response.
- Invalid requests (e.g. non-existent IDs, self-linking).

---

## Verification Plan

### Automated Tests
- We will execute the Pytest test suite using `uv run pytest`.
- The test suite will use an in-memory SQLite database (`sqlite:///:memory:`) to ensure no side effects on the development database.

### Manual Verification
- We can run the FastAPI server locally using `uv run uvicorn main:app --reload` and query the visual Swagger UI documentation at `http://127.0.0.1:8000/docs` to manually verify endpoints.
