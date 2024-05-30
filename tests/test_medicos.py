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

def test_create_medico(client):
    response = client.post("/medicos/", json={
        "email": "medico@teste.com",
        "senha": "senha123",
        "nome": "Medico",
        "dt_nascimento": "1980-01-01",
        "crm": "123456789",
        "especialidade": "Cardiologia"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "medico@teste.com"

def test_read_medico(client):
    response = client.get("/medicos/1")
    assert response.status_code == 200
    assert response.json()["email"] == "medico@teste.com"

def test_update_medico(client):
    response = client.put("/medicos/1", json={
        "email": "medico@teste.com",
        "senha": "senha1234",
        "nome": "Medico Atualizado",
        "dt_nascimento": "1980-01-01",
        "crm": "123456789",
        "especialidade": "Cardiologia"
    })
    assert response.status_code == 200
    assert response.json()["nome"] == "Medico Atualizado"

def test_delete_medico(client):
    response = client.delete("/medicos/1")
    assert response.status_code == 200
    assert response.json()["email"] == "medico@teste.com"
