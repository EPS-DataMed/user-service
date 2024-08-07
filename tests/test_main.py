import json
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db, engine, SessionLocal
from app.models.userModel import User
from app.models.doctorModel import Doctor
from app.models.dependentModel import Dependent
from app import utils
from unittest.mock import patch
import pytest
import jwt
import base64
import os
from app import utils
from sqlalchemy.exc import OperationalError


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

def test_patch_user(test_user):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    patch_data = {
        "full_name": "Partially Updated User"
    }
    response = client.patch(f"/user/users/{db_user.id}", json=patch_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Partially Updated User"

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

def test_read_users():
    response = client.get("/user/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_dependent_record(test_user, test_user_2, test_dependent):
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

def test_read_users():
    response = client.get("/user/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_dependent_record(test_user, test_user_2, test_dependent):
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

def test_send_confirmation_email(test_user, test_user_2):
    with TestingSessionLocal() as db:
        db_user_1 = User(
            full_name=test_user["full_name"],
            email=test_user["email"],
            password=test_user["password"],
            birth_date=test_user["birth_date"],
            biological_sex=test_user["biological_sex"]
        )
        db_user_2 = User(
            full_name=test_user_2["full_name"],
            email=test_user_2["email"],
            password=test_user_2["password"],
            birth_date=test_user_2["birth_date"],  
            biological_sex=test_user_2["biological_sex"]
        )
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)

    email_data = {"email": test_user_2["email"]}
    response = client.post(f"/user/dependents/confirm/{db_user_1.id}", json=email_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Email enviado!"

def test_invalid_email_confirmation(test_user):
    with TestingSessionLocal() as db:
        db_user = User(**test_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    email_data = {"email": "invalid@example.com"}
    response = client.post(f"/user/dependents/confirm/{db_user.id}", json=email_data)
    assert response.status_code == 404

def test_verify_password():
    plain_password = "password123"
    decrypted_password = "password123"
    assert utils.verify_password(plain_password, decrypted_password)

    wrong_password = "password321"
    assert not utils.verify_password(wrong_password, decrypted_password)

@patch("app.utils.requests.post")
def test_decrypt_password(mock_post):
    encrypted_password = "encrypted_password"
    decrypted_password = "decrypted_password"

    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"decrypted_message": decrypted_password}

    result = utils.decrypt_password(encrypted_password)
    assert result == decrypted_password

    mock_post.assert_called_once_with(
        os.getenv("URL_DECRYPT"),
        json={"message": encrypted_password, "private_key": os.getenv("PRIVATE_KEY")}
    )

@patch("app.utils.requests.post")
def test_encrypt_password(mock_post):
    password = "password123"
    encrypted_password = "encrypted_password"

    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"encrypted_message": encrypted_password}

    result = utils.encrypt_password(password)
    assert result == encrypted_password

    mock_post.assert_called_once_with(
        os.getenv("URL_CYPHER"),
        json={"message": password, "public_key": os.getenv("PUBLIC_KEY")}
    )

@patch("app.utils.requests.post")
def test_decrypt_password_error(mock_post):
    encrypted_password = "encrypted_password"

    mock_response = mock_post.return_value
    mock_response.status_code = 500

    with pytest.raises(HTTPException) as exc_info:
        utils.decrypt_password(encrypted_password)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error decrypting password"

@patch("app.utils.requests.post")
def test_encrypt_password_error(mock_post):
    password = "password123"

    mock_response = mock_post.return_value
    mock_response.status_code = 500

    with pytest.raises(HTTPException) as exc_info:
        utils.encrypt_password(password)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error encrypting password"

def test_database_url():
    database_url = os.getenv("DATABASE_URL")
    assert database_url, "DATABASE_URL não encontrada. Verifique o arquivo .env."

def test_database_connection():
    try:
        connection = engine.connect()
        connection.close()
    except OperationalError:
        pytest.fail("Não foi possível conectar ao banco de dados. Verifique a DATABASE_URL.")

def test_get_db():
    with SessionLocal() as session:
        assert session.is_active
        session.close()
        assert session.close

def test_get_db_yield():
    db_gen = get_db()
    db = next(db_gen)
    assert db.is_active
    with pytest.raises(StopIteration):
        next(db_gen)

def test_update_dependent_confirmation(test_user, test_user_2, test_dependent):
    with TestingSessionLocal() as db:
        db_user_1 = User(
            full_name=test_user["full_name"],
            email=test_user["email"],
            password=test_user["password"],
            birth_date=test_user["birth_date"],
            biological_sex=test_user["biological_sex"]
        )
        db_user_2 = User(
            full_name=test_user_2["full_name"],
            email=test_user_2["email"],
            password=test_user_2["password"],
            birth_date=test_user_2["birth_date"],
            biological_sex=test_user_2["biological_sex"]
        )
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)

        db_dependent = Dependent(
            user_id=db_user_1.id,
            dependent_id=db_user_2.id,
            confirmed=test_dependent["confirmed"]
        )
        db.add(db_dependent)
        db.commit()
        db.refresh(db_dependent)

    update_confirmation = {"user_id": db_dependent.user_id, "dependent_id": db_dependent.dependent_id, "confirmed": True}
    response = client.put(f"/user/dependents/{db_dependent.user_id}/{db_dependent.dependent_id}", json=update_confirmation)
    assert response.status_code == 200
    assert response.json()["confirmed"] == True


def test_create_dependent_for_user(test_user, test_user_2, test_dependent):
    with TestingSessionLocal() as db:
        db_user_1 = User(
            full_name=test_user["full_name"],
            email=test_user["email"],
            password=test_user["password"],
            birth_date=test_user["birth_date"],
            biological_sex=test_user["biological_sex"]
        )
        db_user_2 = User(
            full_name=test_user_2["full_name"],
            email=test_user_2["email"],
            password=test_user_2["password"],
            birth_date=test_user_2["birth_date"],
            biological_sex=test_user_2["biological_sex"]
        )
        db.add(db_user_1)
        db.add(db_user_2)
        db.commit()
        db.refresh(db_user_1)
        db.refresh(db_user_2)

    response = client.post("/user/dependents", json=test_dependent)
    assert response.status_code == 200
    created_dependent = response.json()
    assert created_dependent["user_id"] == test_dependent["user_id"]
    assert created_dependent["dependent_id"] == test_dependent["dependent_id"]


def test_update_doctor_specialty(test_user, test_doctor):
    with TestingSessionLocal() as db:
        db_user = User(
            full_name=test_user["full_name"],
            email=test_user["email"],
            password=test_user["password"],
            birth_date=test_user["birth_date"],
            biological_sex=test_user["biological_sex"]
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        db_doctor = Doctor(
            user_id=db_user.id,
            crm=test_doctor["crm"],
            specialty=test_doctor["specialty"]
        )
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)

    update_data = {"crm": test_doctor["crm"], "specialty": "Neurologist"}
    response = client.put(f"/user/doctors/{db_doctor.user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["specialty"] == "Neurologist"

def test_update_user_email(test_user):
    with TestingSessionLocal() as db:
        db_user = User(
            full_name=test_user["full_name"],
            email=test_user["email"],
            password=test_user["password"],
            birth_date=test_user["birth_date"],
            biological_sex=test_user["biological_sex"]
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    new_email = {"email": "newemail@example.com"}
    response = client.patch(f"/user/users/{db_user.id}", json=new_email)
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"

