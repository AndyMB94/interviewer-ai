import pytest
from rest_framework.test import APIClient
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
def test_health_returns_ok():
    client = APIClient()
    response = client.get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
@patch("apps.interviews.views.OpenAI")
def test_ask_returns_llm_answer(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="mocked answer"))
    ]

    client = APIClient()
    response = client.post("/api/ask/", {"question": "hello"}, format="json")

    assert response.status_code == 200
    assert response.json() == {"answer": "mocked answer"}


@pytest.mark.django_db
def test_ask_requires_question():
    client = APIClient()
    response = client.post("/api/ask/", {}, format="json")

    assert response.status_code == 400