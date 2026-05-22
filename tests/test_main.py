import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Setup temporary test database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up database structure
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, headers={"X-API-Key": "dev-premium-api-key-2026"})
    app.dependency_overrides.clear()

def test_api_key_protection():
    # Request without key must fail with 403 Forbidden
    with TestClient(app) as test_client:
        response = test_client.get("/tasks")
        assert response.status_code == 403
        assert "Invalid or missing API Key" in response.json()["detail"]
        
    # Request with incorrect key must fail with 403 Forbidden
    with TestClient(app, headers={"X-API-Key": "wrong-key-123"}) as test_client:
        response = test_client.get("/tasks")
        assert response.status_code == 403
        assert "Invalid or missing API Key" in response.json()["detail"]



# --- List CRUD Tests ---

def test_create_list(client):
    response = client.post("/lists", json={"name": "Work", "description": "Professional duties"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert data["description"] == "Professional duties"
    assert "id" in data

def test_get_lists(client):
    client.post("/lists", json={"name": "Personal"})
    client.post("/lists", json={"name": "Work"})
    
    response = client.get("/lists")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {l["name"] for l in data} == {"Personal", "Work"}

def test_get_list_by_id(client):
    create_resp = client.post("/lists", json={"name": "Shopping", "description": "Grocery items"})
    list_id = create_resp.json()["id"]
    
    response = client.get(f"/lists/{list_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Shopping"
    assert data["description"] == "Grocery items"

def test_get_list_not_found(client):
    response = client.get("/lists/999")
    assert response.status_code == 404

def test_update_list(client):
    create_resp = client.post("/lists", json={"name": "Draft"})
    list_id = create_resp.json()["id"]
    
    response = client.put(f"/lists/{list_id}", json={"name": "Finalized", "description": "Done"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Finalized"
    assert data["description"] == "Done"

def test_delete_list(client):
    create_resp = client.post("/lists", json={"name": "To Delete"})
    list_id = create_resp.json()["id"]
    
    del_resp = client.delete(f"/lists/{list_id}")
    assert del_resp.status_code == 200
    
    get_resp = client.get(f"/lists/{list_id}")
    assert get_resp.status_code == 404


# --- Task CRUD & Validation Tests ---

def test_create_task(client):
    response = client.post("/tasks", json={"title": "Write report", "description": "Draft quarterly review"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write report"
    assert data["status"] == "open"
    assert data["list_id"] is None

def test_create_task_with_invalid_status(client):
    # Only 'open' or 'closed' status should be accepted
    response = client.post("/tasks", json={"title": "Invalid Status", "status": "in-progress"})
    assert response.status_code == 422  # Pydantic validation error

def test_get_tasks_filtering(client):
    client.post("/tasks", json={"title": "Task 1", "status": "open"})
    client.post("/tasks", json={"title": "Task 2", "status": "closed"})
    
    # Get all
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Filter open
    response_open = client.get("/tasks?status=open")
    assert len(response_open.json()) == 1
    assert response_open.json()[0]["title"] == "Task 1"
    
    # Filter closed
    response_closed = client.get("/tasks?status=closed")
    assert len(response_closed.json()) == 1
    assert response_closed.json()[0]["title"] == "Task 2"

def test_update_task(client):
    create_resp = client.post("/tasks", json={"title": "Task To Update"})
    task_id = create_resp.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "status": "closed"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["status"] == "closed"


# --- Task Assignment to Lists & Cascade Tests ---

def test_assign_task_to_list(client):
    # 1. Create list and task
    list_resp = client.post("/lists", json={"name": "Work"})
    list_id = list_resp.json()["id"]
    
    task_resp = client.post("/tasks", json={"title": "Job task"})
    task_id = task_resp.json()["id"]
    
    # 2. Assign task to list
    assign_resp = client.post(f"/tasks/{task_id}/assign/{list_id}")
    assert assign_resp.status_code == 200
    assert assign_resp.json()["list_id"] == list_id
    
    # 3. Verify task is shown inside the list endpoint
    get_list_resp = client.get(f"/lists/{list_id}")
    assert get_list_resp.status_code == 200
    list_data = get_list_resp.json()
    assert len(list_data["tasks"]) == 1
    assert list_data["tasks"][0]["id"] == task_id

def test_assign_task_invalid_list(client):
    task_resp = client.post("/tasks", json={"title": "Task"})
    task_id = task_resp.json()["id"]
    
    response = client.post(f"/tasks/{task_id}/assign/999")
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

def test_delete_list_cascade_behavior(client):
    # If a list is deleted, related tasks must have their list_id set to null, NOT be deleted.
    list_resp = client.post("/lists", json={"name": "Temporary"})
    list_id = list_resp.json()["id"]
    
    task_resp = client.post("/tasks", json={"title": "Persist Task", "list_id": list_id})
    task_id = task_resp.json()["id"]
    
    # Delete the list
    del_list_resp = client.delete(f"/lists/{list_id}")
    assert del_list_resp.status_code == 200
    
    # Verify task still exists and its list_id is NULL
    get_task_resp = client.get(f"/tasks/{task_id}")
    assert get_task_resp.status_code == 200
    assert get_task_resp.json()["list_id"] is None


# --- Task Symmetric Linking Tests ---

def test_link_tasks_symmetric(client):
    # 1. Create two tasks
    t1_resp = client.post("/tasks", json={"title": "Task A"})
    t1_id = t1_resp.json()["id"]
    
    t2_resp = client.post("/tasks", json={"title": "Task B"})
    t2_id = t2_resp.json()["id"]
    
    # 2. Link Task A to Task B
    link_resp = client.post(f"/tasks/{t1_id}/link/{t2_id}")
    assert link_resp.status_code == 200
    
    # 3. Verify task A shows task B in links
    get_t1 = client.get(f"/tasks/{t1_id}")
    assert get_t1.status_code == 200
    t1_data = get_t1.json()
    assert len(t1_data["links"]) == 1
    assert t1_data["links"][0]["id"] == t2_id
    
    # 4. Verify task B symmetrically shows task A in links
    get_t2 = client.get(f"/tasks/{t2_id}")
    assert get_t2.status_code == 200
    t2_data = get_t2.json()
    assert len(t2_data["links"]) == 1
    assert t2_data["links"][0]["id"] == t1_id

def test_link_task_to_itself(client):
    t_resp = client.post("/tasks", json={"title": "Single Task"})
    t_id = t_resp.json()["id"]
    
    response = client.post(f"/tasks/{t_id}/link/{t_id}")
    assert response.status_code == 400
    assert "cannot be linked to itself" in response.json()["detail"]

def test_link_non_existent_tasks(client):
    t_resp = client.post("/tasks", json={"title": "Task"})
    t_id = t_resp.json()["id"]
    
    response = client.post(f"/tasks/{t_id}/link/999")
    assert response.status_code == 404


# --- Task Unlink & Unassign Tests ---

def test_unlink_tasks_symmetric(client):
    # 1. Create two tasks and link them
    t1_resp = client.post("/tasks", json={"title": "Task A"})
    t1_id = t1_resp.json()["id"]
    t2_resp = client.post("/tasks", json={"title": "Task B"})
    t2_id = t2_resp.json()["id"]
    
    client.post(f"/tasks/{t1_id}/link/{t2_id}")
    
    # Verify they are linked
    t1_linked = client.get(f"/tasks/{t1_id}").json()
    assert len(t1_linked["links"]) == 1
    
    # 2. Unlink Task A from Task B
    unlink_resp = client.post(f"/tasks/{t1_id}/unlink/{t2_id}")
    assert unlink_resp.status_code == 200
    
    # 3. Verify task A shows 0 links
    get_t1 = client.get(f"/tasks/{t1_id}")
    assert get_t1.status_code == 200
    assert len(get_t1.json()["links"]) == 0
    
    # 4. Verify task B symmetrically shows 0 links
    get_t2 = client.get(f"/tasks/{t2_id}")
    assert get_t2.status_code == 200
    assert len(get_t2.json()["links"]) == 0

def test_unassign_task_from_list(client):
    # 1. Create list and task and assign them
    list_resp = client.post("/lists", json={"name": "Work"})
    list_id = list_resp.json()["id"]
    task_resp = client.post("/tasks", json={"title": "Task A", "list_id": list_id})
    task_id = task_resp.json()["id"]
    
    # Verify assignment
    task_data = client.get(f"/tasks/{task_id}").json()
    assert task_data["list_id"] == list_id
    
    # 2. Unassign task from the list
    unassign_resp = client.post(f"/tasks/{task_id}/unassign")
    assert unassign_resp.status_code == 200
    assert unassign_resp.json()["list_id"] is None
    
    # 3. Verify list no longer has the task
    get_list = client.get(f"/lists/{list_id}")
    assert len(get_list.json()["tasks"]) == 0

