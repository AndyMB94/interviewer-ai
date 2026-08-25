from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
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
