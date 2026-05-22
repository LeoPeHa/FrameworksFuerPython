from fastapi import FastAPI, Depends, HTTPException, status, Security, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List as TypedList, Optional

import models
import schemas
import crud
from database import engine, get_db

# Create all tables on startup (simple approach for SQLite)
models.Base.metadata.create_all(bind=engine)

API_KEY_NAME = "X-API-Key"
API_KEY = "dev-premium-api-key-2026"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(request: Request, api_key: Optional[str] = Security(api_key_header)):
    # Allow Swagger docs, root, and openapi schema to be accessed without API key
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return None
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key (X-API-Key header required)."
        )
    return api_key

app = FastAPI(
    title="Tasks & Lists CRUD Server",
    description="A high-performance premium REST API for managing tasks, lists, and their relationships.",
    version="1.0.0",
    dependencies=[Depends(get_api_key)]
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Tasks & Lists CRUD Server API.",
        "documentation": "/docs"
    }

# --- Tasks Routes ---

@app.get("/tasks", response_model=TypedList[schemas.TaskResponse])
def get_tasks(
    status: Optional[schemas.TaskStatus] = None,
    list_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieve tasks, with optional filtering by status or list_id."""
    return crud.get_tasks(db, status=status, list_id=list_id)

@app.get("/tasks/{id}", response_model=schemas.TaskResponse)
def get_task(id: int, db: Session = Depends(get_db)):
    """Retrieve a specific task by its ID."""
    db_task = crud.get_task(db, task_id=id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found."
        )
    return db_task

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    try:
        return crud.create_task(db, task_data=task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.put("/tasks/{id}", response_model=schemas.TaskResponse)
def update_task(id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task's fields."""
    try:
        db_task = crud.update_task(db, task_id=id, task_update=task)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {id} not found."
            )
        return db_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.delete("/tasks/{id}", status_code=status.HTTP_200_OK)
def delete_task(id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = crud.delete_task(db, task_id=id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found."
        )
    return {"detail": f"Task {id} deleted successfully."}


# --- Lists Routes ---

@app.get("/lists", response_model=TypedList[schemas.ListResponse])
def get_lists(db: Session = Depends(get_db)):
    """Retrieve all lists."""
    return crud.get_lists(db)

@app.get("/lists/{id}", response_model=schemas.ListResponse)
def get_list(id: int, db: Session = Depends(get_db)):
    """Retrieve a specific list by its ID along with its associated tasks."""
    db_list = crud.get_list(db, list_id=id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with ID {id} not found."
        )
    return db_list

@app.post("/lists", response_model=schemas.ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(list_data: schemas.ListCreate, db: Session = Depends(get_db)):
    """Create a new list."""
    return crud.create_list(db, list_data=list_data)

@app.put("/lists/{id}", response_model=schemas.ListResponse)
def update_list(id: int, list_data: schemas.ListUpdate, db: Session = Depends(get_db)):
    """Update a list's fields."""
    db_list = crud.update_list(db, list_id=id, list_update=list_data)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with ID {id} not found."
        )
    return db_list

@app.delete("/lists/{id}", status_code=status.HTTP_200_OK)
def delete_list(id: int, db: Session = Depends(get_db)):
    """Delete a list. Associated tasks will have their list_id set to NULL."""
    db_list = crud.delete_list(db, list_id=id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with ID {id} not found."
        )
    return {"detail": f"List {id} deleted successfully."}


# --- Association & Link Routes ---

@app.post("/tasks/{id}/link/{other_id}", response_model=schemas.TaskResponse)
def link_tasks(id: int, other_id: int, db: Session = Depends(get_db)):
    """Link two tasks together. This establishes a symmetric, bi-directional relationship."""
    try:
        db_task = crud.link_tasks(db, task_id=id, other_id=other_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"One or both of tasks with IDs {id} and {other_id} could not be found."
            )
        return db_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/tasks/{id}/assign/{list_id}", response_model=schemas.TaskResponse)
def assign_task(id: int, list_id: int, db: Session = Depends(get_db)):
    """Assign a task to a list."""
    try:
        db_task = crud.assign_task_to_list(db, task_id=id, list_id=list_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {id} not found."
            )
        return db_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/tasks/{id}/unlink/{other_id}", response_model=schemas.TaskResponse)
def unlink_tasks(id: int, other_id: int, db: Session = Depends(get_db)):
    """Unlink two tasks. This removes the symmetric, bi-directional relationship."""
    db_task = crud.unlink_tasks(db, task_id=id, other_id=other_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both of tasks with IDs {id} and {other_id} could not be found."
        )
    return db_task

@app.post("/tasks/{id}/unassign", response_model=schemas.TaskResponse)
def unassign_task(id: int, db: Session = Depends(get_db)):
    """Remove a task from its assigned list (setting list_id to NULL)."""
    db_task = crud.unassign_task_from_list(db, task_id=id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found."
        )
    return db_task

