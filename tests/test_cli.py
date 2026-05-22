import pytest
from unittest.mock import MagicMock, patch
import cli

class DummyArgs:
    def __init__(self, **kwargs):
        self.url = "http://127.0.0.1:8000"
        self.api_key = "dev-premium-api-key-2026"
        for k, v in kwargs.items():
            setattr(self, k, v)

@patch("cli.httpx.Client")
def test_cli_task_list(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "title": "Test Task", "status": "open", "list_id": 2, "links": [{"id": 3, "title": "Linked"}], "description": "Task desc"}
    ]
    mock_client.get.return_value = mock_resp
    
    args = DummyArgs(status="open", list_id=2)
    cli.handle_task_list(args)
    
    # Verify client initialization with correct headers
    mock_client_class.assert_called_once_with(
        base_url="http://127.0.0.1:8000",
        headers={"X-API-Key": "dev-premium-api-key-2026"},
        timeout=10.0
    )
    mock_client.get.assert_called_once_with("/tasks", params={"status": "open", "list_id": 2})


@patch("cli.httpx.Client")
def test_cli_task_get(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "id": 1, "title": "Single Task", "status": "open", "list_id": None, "links": [], "description": "Get desc"
    }
    mock_client.get.return_value = mock_resp
    
    args = DummyArgs(id=1)
    cli.handle_task_get(args)
    
    mock_client.get.assert_called_once_with("/tasks/1")

@patch("cli.httpx.Client")
def test_cli_task_create(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 4}
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(title="New CLI Task", desc="CLI created task", status="open", list_id=5)
    cli.handle_task_create(args)
    
    mock_client.post.assert_called_once_with(
        "/tasks", 
        json={"title": "New CLI Task", "description": "CLI created task", "status": "open", "list_id": 5}
    )

@patch("cli.httpx.Client")
def test_cli_task_link(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(id=10, other_id=20)
    cli.handle_task_link(args)
    
    mock_client.post.assert_called_once_with("/tasks/10/link/20")

@patch("cli.httpx.Client")
def test_cli_task_unlink(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(id=10, other_id=20)
    cli.handle_task_unlink(args)
    
    mock_client.post.assert_called_once_with("/tasks/10/unlink/20")

@patch("cli.httpx.Client")
def test_cli_task_assign(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(id=1, list_id=2)
    cli.handle_task_assign(args)
    
    mock_client.post.assert_called_once_with("/tasks/1/assign/2")

@patch("cli.httpx.Client")
def test_cli_task_unassign(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(id=1)
    cli.handle_task_unassign(args)
    
    mock_client.post.assert_called_once_with("/tasks/1/unassign")

@patch("cli.httpx.Client")
def test_cli_list_create(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 3}
    mock_client.post.return_value = mock_resp
    
    args = DummyArgs(name="Work list", desc="Work tasks description")
    cli.handle_list_create(args)
    
    mock_client.post.assert_called_once_with(
        "/lists",
        json={"name": "Work list", "description": "Work tasks description"}
    )
