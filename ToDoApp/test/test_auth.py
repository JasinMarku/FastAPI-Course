from .utils import *
from ..routers.auth import get_current_user, get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, 'jjkkll90', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('wrong_username', 'jjkkll90', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrong_password', db)
    assert wrong_password_user is False

def test_create_access_token():
    username = 'jasin.marku'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'jasin.marku', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)
    user = await get_current_user(token = token)
    assert user == {'username': 'jasin.marku', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token = token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user'