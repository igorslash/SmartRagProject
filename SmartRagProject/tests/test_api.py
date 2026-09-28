import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Импортируем наше приложение
from app.main import app

# Создаём тестовый клиент
client = TestClient(app)


# === ТЕСТ 1: Проверка здоровья (Health Check) ===
def test_health_check():
    """Эндпоинт /health должен возвращать статус 200."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


# === ТЕСТ 2: Запрос без загруженного индекса ===
def test_ask_without_index():
    """Если индекс не загружен, API должен вернуть ошибку, а не упасть с 500."""
    
    # Мы используем mock, чтобы притвориться, что индекс равен None
    with patch("app.endpoints.get_index", return_value=None):
        response = client.post("/ask", json={
            "question": "Какой опыт работы?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Индекс не загружен."


# === ТЕСТ 3: Успешный запрос (с моком RAG-движка) ===
def test_ask_success():
    """Проверяем, что API правильно формирует ответ, если RAG отработал."""
    
    # Создаём фейковый ответ от LlamaIndex
    mock_response = MagicMock()
    mock_response.response = "Опыт работы 5 лет."
    
    # Фейковый source node
    mock_node = MagicMock()
    mock_node.score = 0.85
    mock_node.metadata = {"document_title": "Резюме"}
    mock_response.source_nodes = [mock_node]
    
    # Подменяем реальный query_index на нашу заглушку
    # Это важно: мы НЕ тестируем LlamaIndex или Ollama. 
    # Мы тестируем НАШ API-слой (endpoints.py).
    with patch("app.endpoints.get_index", return_value=MagicMock()):
        with patch("app.endpoints.query_index", return_value=mock_response):
            
            response = client.post("/ask", json={
                "question": "Какой опыт работы?",
                "title_filter": "Резюме"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Проверяем контракт Pydantic-модели AnswerResponse
            assert data["answer"] == "Опыт работы 5 лет."
            assert data["sources_count"] == 1
            assert data["matched_titles"] == ["Резюме"]
            assert data["confidence"] == "high"  # Потому что score 0.85 > 0.7