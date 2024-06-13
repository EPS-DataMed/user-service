from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "birth_date": "1990-01-01",
        "biological_sex": "M"
    }

@pytest.fixture
def test_user_2():
    return {
        "full_name": "Test User 2",
        "email": "testuser2@example.com",
        "password": "testpassword2",
        "birth_date": "1992-01-01",
        "biological_sex": "F"
    }

@pytest.fixture
def test_doctor():
    return {
        "user_id": 1,
        "crm": "123456",
        "specialty": "Cardiologist"
    }

@pytest.fixture
def test_dependent():
    return {
        "user_id": 1,
        "dependent_id": 2,
        "confirmed": False
    }

def test_create_user(test_user):
    response = client.post("/user/users", json=test_user)
    assert response.status_code == 200, response.text
    assert response.json()["email"] == test_user["email"]

def test_create_user_validation_error():
    invalid_user = {
        "full_name": "Test User",
        "email": "invalid-email",
        "password": "short",
        "birth_date": "1990-01-01",
        "biological_sex": "X"
    }
    response = client.post("/user/users", json=invalid_user)
    assert response.status_code == 422, response.text

def test_read_user(test_user):
    client.post("/user/users", json=test_user)
    response = client.get("/user/users")
    assert response.status_code == 200
    
    users = response.json()
    user_found = False
    for user in users:
        if user["id"] == 1:
            user_found = True
            break

    assert user_found

def test_read_user_not_found():
    response = client.get("/user/users/999")
    assert response.status_code == 404

def test_update_user(test_user):
    client.post("/user/users", json=test_user)
    update_data = {
        "full_name": "Updated User",
        "email": "updateduser@example.com",
        "birth_date": "1990-01-01",
        "biological_sex": "M"
    }
    response = client.put("/user/users/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated User"

def test_delete_user(test_user):
    client.post("/user/users", json=test_user)
    response = client.delete("/user/users/1")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_create_doctor(test_user, test_doctor):
    client.post("/user/users", json=test_user)
    response = client.post("/user/doctors", json=test_doctor)
    assert response.status_code == 200, response.text
    assert response.json()["crm"] == test_doctor["crm"]

def test_create_doctor_validation_error():
    invalid_doctor = {
        "user_id": 999, 
        "crm": "",
        "specialty": ""
    }
    response = client.post("/user/doctors", json=invalid_doctor)
    assert response.status_code == 400, response.text

def test_read_doctor(test_user, test_doctor):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_doctor)
    response = client.get("/user/doctors/1")
    assert response.status_code == 200
    assert response.json()["user_id"] == 1

def test_read_doctor_not_found():
    response = client.get("/user/doctors/999")
    assert response.status_code == 404

def test_update_doctor(test_user, test_doctor):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_doctor)
    update_data = {
        "crm": "654321",
        "specialty": "Neurologist"
    }
    response = client.put("/user/doctors/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["crm"] == "654321"

def test_delete_doctor(test_user, test_doctor):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_doctor)
    response = client.delete("/user/doctors/1")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_create_dependent(test_user, test_user_2, test_dependent):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2)
    response = client.post("/user/dependents", json=test_dependent)
    assert response.status_code == 200, response.text
    assert response.json()["dependent_id"] == test_dependent["dependent_id"]

def test_create_dependent_validation_error():
    invalid_dependent = {
        "user_id": 1,
        "dependent_id": 1,
        "confirmed": "invalid"
    }
    response = client.post("/user/dependents", json=invalid_dependent)
    assert response.status_code == 422, response.text

def test_read_dependent(test_user, test_user_2, test_dependent):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2) 
    client.post("/user/dependents", json=test_dependent)
    response = client.get("/user/dependents/1/2")
    assert response.status_code == 200
    assert response.json()["dependent_id"] == 2

def test_read_dependent_not_found():
    response = client.get("/user/dependents/1/999")
    assert response.status_code == 404

def test_update_dependent(test_user, test_user_2, test_dependent):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2)
    client.post("/user/dependents", json=test_dependent)
    update_data = {
        "dependent_id": 2,
        "confirmed": True
    }
    response = client.put("/user/dependents/1/2", json=update_data)
    assert response.status_code == 200
    assert response.json()["confirmed"] == True

def test_delete_dependent(test_user, test_user_2, test_dependent):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2) 
    client.post("/user/dependents", json=test_dependent)
    response = client.delete("/user/dependents/1/2")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}
