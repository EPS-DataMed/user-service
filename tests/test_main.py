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
        "nome_completo": "Test User",
        "email": "testuser@example.com",
        "senha": "testpassword",
        "data_nascimento": "1990-01-01",
        "sexo_biologico": "M",
        "formulario": {},
        "status_formulario": "Não iniciado"
    }

@pytest.fixture
def test_user_2():
    return {
        "nome_completo": "Test User 2",
        "email": "testuser2@example.com",
        "senha": "testpassword2",
        "data_nascimento": "1992-01-01",
        "sexo_biologico": "F",
        "formulario": {},
        "status_formulario": "Não iniciado"
    }

@pytest.fixture
def test_medico():
    return {
        "id_usuario": 1,
        "crm": "123456",
        "especialidade": "Cardiologista"
    }

@pytest.fixture
def test_dependente():
    return {
        "id_usuario": 1,
        "id_dependente": 2,
        "confirmado": False
    }

def test_create_user(test_user):
    response = client.post("/user/users", json=test_user)
    assert response.status_code == 200, response.text
    assert response.json()["email"] == test_user["email"]

def test_create_user_validation_error():
    invalid_user = {
        "nome_completo": "Test User",
        "email": "invalid-email",
        "senha": "short",
        "data_nascimento": "1990-01-01",
        "sexo_biologico": "X",
        "formulario": {},
        "status_formulario": "Invalid"
    }
    response = client.post("/user/users", json=invalid_user)
    assert response.status_code == 422, response.text

def test_read_user(test_user):
    client.post("/user/users", json=test_user)
    response = client.get("/user/users")
    assert response.status_code == 200
    
    usuarios = response.json()
    usuario_encontrado = False
    for usuario in usuarios:
        if usuario["id"] == 1:
            usuario_encontrado = True
            break

    assert usuario_encontrado


def test_read_user_not_found():
    response = client.get("/user/users/999")
    assert response.status_code == 404

def test_update_user(test_user):
    client.post("/user/users", json=test_user)
    update_data = {
        "nome_completo": "Updated User",
        "email": "updateduser@example.com",
        "data_nascimento": "1990-01-01",
        "sexo_biologico": "M",
        "formulario": {},
        "status_formulario": "Não iniciado"
    }
    response = client.put("/user/users/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["nome_completo"] == "Updated User"

def test_delete_user(test_user):
    client.post("/user/users", json=test_user)
    response = client.delete("/user/users/1")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_create_medico(test_user, test_medico):
    client.post("/user/users", json=test_user)
    response = client.post("/user/doctors", json=test_medico)
    assert response.status_code == 200, response.text
    assert response.json()["crm"] == test_medico["crm"]

def test_create_medico_validation_error():
    invalid_medico = {
        "id_usuario": 999, 
        "crm": "",
        "especialidade": ""
    }
    response = client.post("/user/doctors", json=invalid_medico)
    assert response.status_code == 400, response.text

def test_read_medico(test_user, test_medico):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_medico)
    response = client.get("/user/doctors/1")
    assert response.status_code == 200
    assert response.json()["id_usuario"] == 1

def test_read_medico_not_found():
    response = client.get("/user/doctors/999")
    assert response.status_code == 404

def test_update_medico(test_user, test_medico):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_medico)
    update_data = {
        "crm": "654321",
        "especialidade": "Neurologista"
    }
    response = client.put("/user/doctors/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["crm"] == "654321"

def test_delete_medico(test_user, test_medico):
    client.post("/user/users", json=test_user)
    client.post("/user/doctors", json=test_medico)
    response = client.delete("/user/doctors/1")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}

def test_create_dependente(test_user, test_user_2, test_dependente):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2)
    response = client.post("/user/dependents", json=test_dependente)
    assert response.status_code == 200, response.text
    assert response.json()["id_dependente"] == test_dependente["id_dependente"]

def test_create_dependente_validation_error():
    invalid_dependente = {
        "id_usuario": 1,
        "id_dependente": 1,
        "confirmado": "invalid"
    }
    response = client.post("/user/dependents", json=invalid_dependente)
    assert response.status_code == 422, response.text

def test_read_dependente(test_user, test_user_2, test_dependente):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2) 
    client.post("/user/dependents", json=test_dependente)
    response = client.get("/user/dependents/1/2")
    assert response.status_code == 200
    assert response.json()["id_dependente"] == 2

def test_read_dependente_not_found():
    response = client.get("/user/dependents/1/999")
    assert response.status_code == 404

def test_update_dependente(test_user, test_user_2, test_dependente):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2)  # Create a second user
    client.post("/user/dependents", json=test_dependente)
    update_data = {
        "id_dependente": 2,
        "confirmado": True
    }
    response = client.put("/user/dependents/1/2", json=update_data)
    assert response.status_code == 200
    assert response.json()["confirmado"] == True

def test_delete_dependente(test_user, test_user_2, test_dependente):
    client.post("/user/users", json=test_user)
    client.post("/user/users", json=test_user_2) 
    client.post("/user/dependents", json=test_dependente)
    response = client.delete("/user/dependents/1/2")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}
