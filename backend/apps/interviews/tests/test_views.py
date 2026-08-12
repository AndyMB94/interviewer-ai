import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient
from unittest.mock import MagicMock, patch
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.interviews.models import Answer, Interview, Question
from apps.recruiting.models import Postulacion, Puesto


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
    data = response.json()
    assert data["task_id"] == "fake-task-id"
    assert "interview_id" in data


@pytest.mark.django_db
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_without_authentication_creates_interview_without_user(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    client = APIClient()
    response = client.post("/api/ask/", {"question": "hello"}, format="json")

    interview = Interview.objects.get(id=response.json()["interview_id"])
    assert interview.user is None


@pytest.mark.django_db
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_authenticated_creates_interview_with_user(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result
    user = User.objects.create_user("postulante1", password="testpass123")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/ask/", {"question": "hello"}, format="json")

    interview = Interview.objects.get(id=response.json()["interview_id"])
    assert interview.user == user


@pytest.mark.django_db
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_links_the_postulacion_id_sent_explicitly(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )
    user = User.objects.create_user("andy@example.com", email="andy@example.com", password="testpass123")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/ask/", {"question": "hello", "postulacion_id": postulacion.id}, format="json"
    )

    interview = Interview.objects.get(id=response.json()["interview_id"])
    assert interview.postulacion == postulacion


@pytest.mark.django_db
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_without_postulacion_id_does_not_guess_it(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )
    user = User.objects.create_user("andy@example.com", email="andy@example.com", password="testpass123")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/ask/", {"question": "hello"}, format="json")

    interview = Interview.objects.get(id=response.json()["interview_id"])
    assert interview.postulacion is None


@pytest.mark.django_db
@patch("apps.interviews.views.ask_llm_task.delay")
def test_ask_rejects_postulacion_that_already_has_an_interview(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )
    Interview.objects.create(postulacion=postulacion)
    user = User.objects.create_user("andy@example.com", email="andy@example.com", password="testpass123")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/ask/", {"question": "hello", "postulacion_id": postulacion.id}, format="json"
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_ask_rejects_postulacion_id_that_does_not_belong_to_the_user():
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )
    otro_user = User.objects.create_user(
        "otro@example.com", email="otro@example.com", password="testpass123"
    )

    client = APIClient()
    client.force_authenticate(user=otro_user)
    response = client.post(
        "/api/ask/", {"question": "hello", "postulacion_id": postulacion.id}, format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_ask_rejects_postulacion_id_when_anonymous():
    client = APIClient()
    response = client.post("/api/ask/", {"question": "hello", "postulacion_id": 99999}, format="json")

    assert response.status_code == 401


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


@pytest.mark.django_db
@patch("apps.interviews.views.transcribe_audio_task.delay")
def test_transcribe_returns_task_id(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    audio_file = SimpleUploadedFile("audio.wav", b"fake-audio-bytes", content_type="audio/wav")

    client = APIClient()
    response = client.post("/api/transcribe/", {"audio": audio_file}, format="multipart")

    assert response.status_code == 202
    assert response.json() == {"task_id": "fake-task-id"}


@pytest.mark.django_db
def test_transcribe_requires_audio_file():
    client = APIClient()
    response = client.post("/api/transcribe/", {}, format="multipart")

    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.interviews.views.AsyncResult")
def test_transcribe_result_done(mock_async_result_class):
    mock_result = MagicMock()
    mock_result.ready.return_value = True
    mock_result.result = "hola mundo"
    mock_async_result_class.return_value = mock_result

    client = APIClient()
    response = client.get("/api/transcribe/some-task-id/")

    assert response.status_code == 200
    assert response.json() == {"status": "done", "transcript": "hola mundo"}


@pytest.mark.django_db
@patch("apps.interviews.views.synthesize_speech_task.delay")
def test_speak_returns_task_id(mock_delay):
    mock_result = MagicMock()
    mock_result.id = "fake-task-id"
    mock_delay.return_value = mock_result

    client = APIClient()
    response = client.post("/api/speak/", {"text": "hola"}, format="json")

    assert response.status_code == 202
    assert response.json() == {"task_id": "fake-task-id"}


@pytest.mark.django_db
def test_speak_requires_text():
    client = APIClient()
    response = client.post("/api/speak/", {}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.interviews.views.AsyncResult")
def test_speak_result_done(mock_async_result_class):
    mock_result = MagicMock()
    mock_result.ready.return_value = True
    mock_result.result = "/media/abc123.mp3"
    mock_async_result_class.return_value = mock_result

    client = APIClient()
    response = client.get("/api/speak/some-task-id/")

    assert response.status_code == 200
    assert response.json() == {"status": "done", "audio_url": "/media/abc123.mp3"}


@pytest.mark.django_db
def test_finish_interview_marks_status_as_finished():
    interview = Interview.objects.create()

    client = APIClient()
    response = client.post(f"/api/interviews/{interview.id}/finish/")

    assert response.status_code == 200
    interview.refresh_from_db()
    assert interview.status == Interview.Status.FINISHED


@pytest.mark.django_db
def test_finish_interview_404_for_unknown_id():
    client = APIClient()
    response = client.post("/api/interviews/99999/finish/")

    assert response.status_code == 404


@pytest.fixture
def interview_con_postulacion():
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
        resultado_filtro="Buen fit para el puesto.",
    )
    interview = Interview.objects.create(postulacion=postulacion)
    question = Question.objects.create(interview=interview, text="¿Cuál es tu experiencia con Django?")
    Answer.objects.create(question=question, text="Cinco años.")
    return reclutador, interview


@pytest.mark.django_db
def test_interview_detail_owner_reclutador_sees_full_transcript(interview_con_postulacion):
    reclutador, interview = interview_con_postulacion

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get(f"/api/interviews/{interview.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["postulacion"]["nombre"] == "Andy"
    assert data["postulacion"]["puesto_titulo"] == "Dev Backend"
    assert data["postulacion"]["resultado_filtro"] == "Buen fit para el puesto."
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question"] == "¿Cuál es tu experiencia con Django?"
    assert data["questions"][0]["answer"] == "Cinco años."


@pytest.mark.django_db
def test_interview_detail_forbidden_for_other_reclutador(interview_con_postulacion):
    _, interview = interview_con_postulacion
    otro_reclutador = User.objects.create_user("reclutador2", password="testpass123")
    otro_reclutador.groups.add(Group.objects.get(name="Reclutador"))

    client = APIClient()
    client.force_authenticate(user=otro_reclutador)
    response = client.get(f"/api/interviews/{interview.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_interview_detail_requires_authentication(interview_con_postulacion):
    _, interview = interview_con_postulacion

    client = APIClient()
    response = client.get(f"/api/interviews/{interview.id}/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_interview_detail_forbidden_without_postulacion():
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    interview = Interview.objects.create()

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get(f"/api/interviews/{interview.id}/")

    assert response.status_code == 403