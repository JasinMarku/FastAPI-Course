from fastapi import status
from ..routers.todos import get_db, get_current_user
from ..models import Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'complete': False, 'title': 'Finish testing section',
         'description': 'Need to get better everyday', 'id' : 1,
         'priority': 5, 'owner_id': 1
         }]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Finish testing section',
         'description': 'Need to get better everyday', 'id' : 1,
         'priority': 5, 'owner_id': 1
         }

def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_create_todo(test_todo):
    # Define the request payload for creating a new to-do item
    request_data = {'title': 'Finish testing section',
                    'description': 'Need to get better everyday',
                    'priority': 5,
                    'complete': False,
                    }

    # Send a POST request to create a new to-do
    response = client.post('/todos/todo/', json=request_data)

    # Ensure the response status code is 201 (Created)
    assert response.status_code == 201

    # Open a new database session to verify that the todo was added
    db = TestingSessionLocal()

    # Query the database for the new to-do (assuming its ID is 2)
    model = db.query(Todos).filter(Todos.id ==  2).first()

    # Validate that the stored data matches the request data
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todo):
    request_data = {
        'title': 'Finish testing section',
        'description': 'Need to get better everyday',
        'priority': 5,
        'complete': False,
    }

    response = client.put("/todos/todo/1", json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Finish testing section'

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Finish testing section',
        'description': 'Need to get better everyday',
        'priority': 5,
        'complete': False,
    }

    response = client.put("/todos/todo/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found'}

def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found():
    response = client.delete('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found'}























