import pytest
from datetime import datetime, timedelta

def test_fr_001_register_returns_jwt(client):
    response = client.post("/api/auth/register", json={"email": "testuser1@example.com", "password": "password123"})
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_fr_002_login_returns_jwt(client):
    client.post("/api/auth/register", json={"email": "testuser2@example.com", "password": "password123"})
    response = client.post("/api/auth/login", json={"email": "testuser2@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_fr_003_create_todo_returns_created_object(client, auth_headers):
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    response = client.post("/api/todos", json=todo_data, headers=auth_headers)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == todo_data["title"]
    assert response_data["description"] == todo_data["description"]
    assert response_data["due_date"] == todo_data["due_date"]
    assert response_data["completed"] == todo_data["completed"]

def test_fr_004_list_todos_returns_all_todos(client, auth_headers):
    todo_data_1 = {
        "title": "Todo 1",
        "description": "First todo.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    todo_data_2 = {
        "title": "Todo 2",
        "description": "Second todo.",
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "completed": True
    }
    client.post("/api/todos", json=todo_data_1, headers=auth_headers)
    client.post("/api/todos", json=todo_data_2, headers=auth_headers)
    response = client.get("/api/todos", headers=auth_headers)
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 2

def test_fr_005_filter_todos_by_completed_status(client, auth_headers):
    client.post("/api/todos", json={"title": "Incomplete Todo", "description": "Not done", "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(), "completed": False}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Completed Todo", "description": "Done", "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(), "completed": True}, headers=auth_headers)
    response = client.get("/api/todos?completed=true", headers=auth_headers)
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["completed"] is True

def test_fr_006_get_todo_by_id(client, auth_headers):
    todo_data = {
        "title": "Specific Todo",
        "description": "Retrieve this todo.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    create_response = client.post("/api/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    response = client.get(f"/api/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

def test_fr_007_update_todo(client, auth_headers):
    todo_data = {
        "title": "Original Title",
        "description": "Original description.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    create_response = client.post("/api/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description.",
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "completed": True
    }
    update_response = client.put(f"/api/todos/{todo_id}", json=updated_data, headers=auth_headers)
    assert update_response.status_code == 200
    updated_todo = update_response.json()
    assert updated_todo["title"] == updated_data["title"]
    assert updated_todo["description"] == updated_data["description"]
    assert updated_todo["due_date"] == updated_data["due_date"]
    assert updated_todo["completed"] == updated_data["completed"]

def test_fr_008_toggle_todo_completed_status(client, auth_headers):
    todo_data = {
        "title": "Toggle Todo",
        "description": "Toggle this todo.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    create_response = client.post("/api/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    toggle_response = client.patch(f"/api/todos/{todo_id}", json={"completed": True}, headers=auth_headers)
    assert toggle_response.status_code == 200
    assert toggle_response.json()["completed"] is True

def test_fr_009_delete_todo(client, auth_headers):
    todo_data = {
        "title": "Delete Todo",
        "description": "This todo will be deleted.",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "completed": False
    }
    create_response = client.post("/api/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    delete_response = client.delete(f"/api/todos/{todo_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    get_response = client.get(f"/api/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 404