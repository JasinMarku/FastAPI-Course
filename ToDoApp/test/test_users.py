from .utils import *
from ..main import app
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'jasin.marku'
    assert response.json()['email'] == 'jasinmarku@gmail.com'
    assert response.json()['first_name'] == 'Jasin'
    assert response.json()['last_name'] == 'Marku'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '9293210497'

def test_change_password_success(test_user):
    response = client.put("/users/change-password", data={"old_password": "jjkkll90", 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = client.put("/users/change-password", data={"old_password": "wrong_password", 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect Old Password'}

def test_change_phone_number_success(test_user):
    response = client.put("/users/update-phone-number", json={'phone_number': '1234567890'})
    assert response.status_code == status.HTTP_204_NO_CONTENT