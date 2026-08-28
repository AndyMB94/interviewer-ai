from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.recruiting.models import Postulacion, Puesto


@pytest.fixture
def reclutador():
    user = User.objects.create_user("reclutador1", password="testpass123")
    user.groups.add(Group.objects.get(name="Reclutador"))
    return user


@pytest.fixture
def otro_reclutador():
    user = User.objects.create_user("reclutador2", password="testpass123")
    user.groups.add(Group.objects.get(name="Reclutador"))
    return user


@pytest.fixture
def puesto(reclutador):
    return Puesto.objects.create(
        titulo="Desarrollador Backend",
        descripcion="Buscamos alguien con experiencia en Django.",
        requisitos="Python, Django, PostgreSQL.",
        creado_por=reclutador,
    )


def _fake_pdf(nombre="cv.pdf"):
    return SimpleUploadedFile(nombre, b"contenido de prueba", content_type="application/pdf")


@pytest.mark.django_db
def test_entrevista_vencida_is_false_when_no_deadline_set(puesto):
    postulacion = Postulacion.objects.create(
        puesto=puesto, nombre="Andy", email="andy@example.com", cv=_fake_pdf()
    )

    assert postulacion.entrevista_vencida is False


@pytest.mark.django_db
def test_entrevista_vencida_is_true_after_deadline(puesto):
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        fecha_limite_entrevista=timezone.now() - timedelta(days=1),
    )

    assert postulacion.entrevista_vencida is True


@pytest.mark.django_db
def test_entrevista_vencida_is_false_before_deadline(puesto):
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        fecha_limite_entrevista=timezone.now() + timedelta(days=1),
    )

    assert postulacion.entrevista_vencida is False


@pytest.mark.django_db
@patch("apps.recruiting.views.screen_postulacion_task.delay")
def test_anyone_can_postular_without_an_account(mock_delay, puesto):
    client = APIClient()
    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy Mallcco", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    assert response.status_code == 201
    postulacion = Postulacion.objects.get(id=response.json()["id"])
    assert postulacion.estado == Postulacion.Estado.PENDIENTE
    mock_delay.assert_called_once_with(postulacion.id)


@pytest.mark.django_db
def test_postular_to_a_puesto_cerrado_is_rejected(puesto):
    puesto.estado = Puesto.Estado.CERRADO
    puesto.save()

    client = APIClient()
    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    assert response.status_code == 400
    assert Postulacion.objects.count() == 0


@pytest.mark.django_db
def test_postular_with_non_pdf_file_fails(puesto):
    client = APIClient()
    archivo = SimpleUploadedFile("cv.txt", b"no es un pdf", content_type="text/plain")
    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": archivo},
        format="multipart",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_anonymous_cannot_list_postulaciones():
    client = APIClient()
    response = client.get("/api/postulaciones/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_reclutador_only_sees_postulaciones_of_their_own_puestos(puesto, reclutador, otro_reclutador):
    Postulacion.objects.create(puesto=puesto, nombre="Andy", email="andy@example.com", cv=_fake_pdf())

    client = APIClient()
    client.force_authenticate(user=otro_reclutador)
    response = client.get("/api/postulaciones/")

    assert response.status_code == 200
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_owner_reclutador_sees_postulaciones_of_their_puesto(puesto, reclutador):
    Postulacion.objects.create(puesto=puesto, nombre="Andy", email="andy@example.com", cv=_fake_pdf())

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["puesto_titulo"] == puesto.titulo
    assert data[0]["interview_id"] is None


@pytest.mark.django_db
def test_postulacion_list_includes_interview_id_when_it_has_one(puesto, reclutador):
    from apps.interviews.models import Interview

    postulacion = Postulacion.objects.create(
        puesto=puesto, nombre="Andy", email="andy@example.com", cv=_fake_pdf()
    )
    interview = Interview.objects.create(postulacion=postulacion)

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/")

    assert response.status_code == 200
    assert response.json()["results"][0]["interview_id"] == interview.id


@pytest.mark.django_db
def test_search_matches_nombre_case_insensitive_and_partial(puesto, reclutador):
    Postulacion.objects.create(puesto=puesto, nombre="Andy Mallcco", email="andy@example.com", cv=_fake_pdf())
    Postulacion.objects.create(puesto=puesto, nombre="Carla Ruiz", email="carla@example.com", cv=_fake_pdf())

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/?search=MALLCCO")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["nombre"] == "Andy Mallcco"


@pytest.mark.django_db
def test_search_matches_email(puesto, reclutador):
    Postulacion.objects.create(puesto=puesto, nombre="Andy Mallcco", email="andy@example.com", cv=_fake_pdf())
    Postulacion.objects.create(puesto=puesto, nombre="Carla Ruiz", email="carla@example.com", cv=_fake_pdf())

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/?search=carla@example")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["email"] == "carla@example.com"


@pytest.mark.django_db
def test_search_without_match_returns_empty_list(puesto, reclutador):
    Postulacion.objects.create(puesto=puesto, nombre="Andy Mallcco", email="andy@example.com", cv=_fake_pdf())

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/?search=inexistente")

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_estado_filter(puesto, reclutador):
    aprobada = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Carla Ruiz",
        email="carla@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.RECHAZADO,
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/?estado=aprobado")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == aprobada.id


@pytest.mark.django_db
def test_search_and_estado_combined(puesto, reclutador):
    aprobada = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Rechazado",
        email="andy2@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.RECHAZADO,
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/postulaciones/?search=andy&estado=aprobado")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == aprobada.id


@pytest.mark.django_db
@patch("apps.recruiting.views.screen_postulacion_task.delay")
def test_cannot_postular_twice_to_the_same_puesto_with_the_same_email(mock_delay, puesto):
    client = APIClient()
    client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy Mallcco", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy Mallcco", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    assert response.status_code == 400
    assert "email" in response.json()
    assert Postulacion.objects.count() == 1


@pytest.mark.django_db
@patch("apps.recruiting.views.screen_postulacion_task.delay")
def test_email_is_normalized_so_case_cannot_bypass_the_duplicate_check(mock_delay, puesto):
    client = APIClient()
    client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy Mallcco", "email": "Andy@Example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy Mallcco", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    assert response.status_code == 400
    assert Postulacion.objects.count() == 1


@pytest.mark.django_db
@patch("apps.recruiting.views.screen_postulacion_task.delay")
def test_same_email_can_postular_to_a_different_puesto(mock_delay, puesto, reclutador):
    otro_puesto = Puesto.objects.create(
        titulo="Otro puesto", descripcion="...", requisitos="...", creado_por=reclutador
    )
    client = APIClient()
    r1 = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )
    r2 = client.post(
        "/api/postulaciones/",
        {"puesto": otro_puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": _fake_pdf()},
        format="multipart",
    )

    assert r1.status_code == 201
    assert r2.status_code == 201


@pytest.mark.django_db
def test_cv_over_the_size_limit_is_rejected(puesto):
    archivo_grande = SimpleUploadedFile(
        "cv.pdf", b"0" * (5 * 1024 * 1024 + 1), content_type="application/pdf"
    )
    client = APIClient()
    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": archivo_grande},
        format="multipart",
    )

    assert response.status_code == 400
    assert Postulacion.objects.count() == 0


@pytest.mark.django_db
@patch("apps.recruiting.views.screen_postulacion_task.delay")
def test_cv_at_the_size_limit_is_accepted(mock_delay, puesto):
    archivo_justo = SimpleUploadedFile("cv.pdf", b"0" * (5 * 1024 * 1024), content_type="application/pdf")
    client = APIClient()
    response = client.post(
        "/api/postulaciones/",
        {"puesto": puesto.id, "nombre": "Andy", "email": "andy@example.com", "cv": archivo_justo},
        format="multipart",
    )

    assert response.status_code == 201
