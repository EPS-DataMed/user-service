import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="function")
def mock_db():
    # Cria mocks para cursor e conexão
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    
    # Retorna o mock_cursor e mock_conn para serem usados no teste
    return mock_cursor, mock_conn

@patch('app.routers.user.get_cursor')
@patch('app.routers.user.get_conn')
def test_create_user(mock_get_conn, mock_get_cursor, mock_db):
    mock_cursor, mock_conn = mock_db
    # Configura os mocks
    mock_get_cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    
    mock_cursor.fetchone.return_value = {
        "id": 5,
        "name": "Test User",
        "email": "test2.user@example.com",
        "password": "password123"
    }
    
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test2.user@example.com", "password": "password123"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test User"
    assert response.json()["email"] == "test2.user@example.com"

    # Verifica se o método execute foi chamado com os argumentos corretos
    mock_cursor.execute.assert_called_once_with(
        """INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id, name, email, password""",
        ("Test User", "test2.user@example.com", "password123")
    )
    mock_conn.commit.assert_called_once()
