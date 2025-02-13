from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..models import Todos, Users
import pytest
from fastapi.testclient import TestClient
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base.metadata.create_all(bind = engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username' : 'jasin.marku', 'id': 1, 'user_role' : 'admin'}

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Finish testing section",
        description="Need to get better everyday",
        priority=5,
        complete=False,
        owner_id=1 ,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username='jasin.marku',
        email='jasinmarku@gmail.com',
        first_name='Jasin',
        last_name='Marku',
        hashed_password=bcrypt_context.hash('jjkkll90'),
        role='admin',
        phone_number='9293210497'
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()












