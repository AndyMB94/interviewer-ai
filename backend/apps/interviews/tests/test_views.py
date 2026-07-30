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
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_returns_task_id(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    client = APIClient()
    response = client.post("/api/ask/", {"question": "hello"}, format="json")

    assert response.status_code == 202
    assert response.json() == {"task_id": "fake-task-id"}


@pytest.mark.django_db
def test_ask_requires_question():
    client = APIClient()
    response = client.post("/api/ask/", {}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.interviews.views.AsyncResult")
def test_ask_result_pending(mock_async_result_class):
    mock_result = MagicMock()
    mock_result.ready.return_value = False
    mock_async_result_class.return_value = mock_result

    client = APIClient()
    response = client.get("/api/ask/some-task-id/")

    assert response.status_code == 200
    assert response.json() == {"status": "pending"}


@pytest.mark.django_db
@patch("apps.interviews.views.AsyncResult")
def test_ask_result_done(mock_async_result_class):
    mock_result = MagicMock()
    mock_result.ready.return_value = True
    mock_result.result = "una respuesta"
    mock_async_result_class.return_value = mock_result

    client = APIClient()
    response = client.get("/api/ask/some-task-id/")

    assert response.status_code == 200
    assert response.json() == {"status": "done", "answer": "una respuesta"}