import json
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.userModel import User
from app.models.doctorModel import Doctor
from app.models.dependentModel import Dependent
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
        "birth_date": date(1990, 1, 1),
        "biological_sex": "M"
    }

@pytest.fixture
def test_user_2():
    return {
        "full_name": "Test User 2",
        "email": "testuser2@example.com",
        "password": "testpassword2",
        "birth_date": date(1992, 1, 1),
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

def test_read_user(test_user):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    response = client.get("/user/users")
    assert response.status_code == 200
    
    users = response.json()
    user_found = any(user["id"] == db_user.id for user in users)

    assert user_found

def test_read_user_not_found():
    response = client.get("/user/users/999")
    assert response.status_code == 404

def test_update_user(test_user):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    update_data = {
        "full_name": "Updated User",
        "email": "updateduser@example.com",
        "birth_date": "1990-01-01",
        "biological_sex": "M"
    }
    response = client.put(f"/user/users/{db_user.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated User"

def test_delete_user(test_user):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    response = client.delete(f"/user/users/{db_user.id}")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_read_doctor(test_user, test_doctor):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        db_doctor = Doctor(**test_doctor)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
    
    response = client.get(f"/user/doctors/{db_doctor.user_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == db_doctor.user_id

def test_read_doctor_not_found():
    response = client.get("/user/doctors/999")
    assert response.status_code == 404

def test_update_doctor(test_user, test_doctor):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        db_doctor = Doctor(**test_doctor)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
    
    update_data = {
        "crm": "654321",
        "specialty": "Neurologist"
    }
    response = client.put(f"/user/doctors/{db_doctor.user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["crm"] == "654321"

def test_delete_doctor(test_user, test_doctor):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        db_doctor = Doctor(**test_doctor)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
    
    response = client.delete(f"/user/doctors/{db_doctor.user_id}")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_create_dependent(test_user, test_user_2, test_dependent):
    with TestingSessionLocal() as db:
        db_user_1 = User(**test_user)
        db_user_2 = User(**test_user_2)
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)
        
        db_dependent = Dependent(**test_dependent)
        db.add(db_dependent)
        db.commit()
        db.refresh(db_dependent)
    
    response = client.get(f"/user/dependents/{db_dependent.user_id}/{db_dependent.dependent_id}")
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
    with TestingSessionLocal() as db:
        db_user_1 = User(**test_user)
        db_user_2 = User(**test_user_2)
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)
        
        db_dependent = Dependent(**test_dependent)
        db.add(db_dependent)
        db.commit()
        db.refresh(db_dependent)
    
    response = client.get(f"/user/dependents/{db_dependent.user_id}/{db_dependent.dependent_id}")
    assert response.status_code == 200
    assert response.json()["dependent_id"] == db_dependent.dependent_id

def test_read_dependent_not_found():
    response = client.get("/user/dependents/1/999")
    assert response.status_code == 404

def test_update_dependent(test_user, test_user_2, test_dependent):
    with TestingSessionLocal() as db:
        db_user_1 = User(**test_user)
        db_user_2 = User(**test_user_2)
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)
        
        db_dependent = Dependent(**test_dependent)
        db.add(db_dependent)
        db.commit()
        db.refresh(db_dependent)
    
    update_data = {
        "dependent_id": 2,
        "confirmed": True
    }
    response = client.put(f"/user/dependents/{db_dependent.user_id}/{db_dependent.dependent_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["confirmed"] == True

def test_delete_dependent(test_user, test_user_2, test_dependent):
    with TestingSessionLocal() as db:
        db_user_1 = User(**test_user)
        db_user_2 = User(**test_user_2)
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)
        
        db_dependent = Dependent(**test_dependent)
        db.add(db_dependent)
        db.commit()
        db.refresh(db_dependent)
    
    response = client.delete(f"/user/dependents/{db_dependent.user_id}/{db_dependent.dependent_id}")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_get_user_with_doctor(test_user, test_doctor):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        db_doctor = Doctor(**test_doctor)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)

        user_id = db_user.id
    
    response = client.get(f"/user/users/with-doctor/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert "doctor" in data
    assert data["doctor"]["crm"] == test_doctor["crm"]
