from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import os
import sys

# Adicione o caminho do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import Base, get_db

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

def test_create_paciente(client):
    response = client.post("/pacientes/", json={
        "email": "teste@teste.com",
        "senha": "senha123",
        "nome": "Teste",
        "dt_nascimento": "2000-01-01",
        "status_formulario": "Preenchido"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "teste@teste.com"

def test_read_paciente(client):
    response = client.get("/pacientes/1")
    assert response.status_code == 200
    assert response.json()["email"] == "teste@teste.com"

def test_update_paciente(client):
    response = client.put("/pacientes/1", json={
        "email": "teste@teste.com",
        "senha": "senha1234",
        "nome": "Teste Atualizado",
        "dt_nascimento": "2000-01-01",
        "status_formulario": "Preenchido"
    })
    assert response.status_code == 200
    assert response.json()["nome"] == "Teste Atualizado"

def test_delete_paciente(client):
    response = client.delete("/pacientes/1")
    assert response.status_code == 200
    assert response.json()["email"] == "teste@teste.com"
