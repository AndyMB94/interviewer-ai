import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient

from apps.recruiting.models import Puesto


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
def postulante():
    user = User.objects.create_user("postulante1", password="testpass123")
    user.groups.add(Group.objects.get(name="Postulante"))
    return user


@pytest.fixture
def puesto(reclutador):
    return Puesto.objects.create(
        titulo="Desarrollador Backend",
        descripcion="Buscamos alguien con experiencia en Django.",
        requisitos="Python, Django, PostgreSQL.",
        creado_por=reclutador,
    )


@pytest.mark.django_db
def test_anyone_can_list_puestos(puesto):
    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_anyone_can_retrieve_a_puesto(puesto):
    client = APIClient()
    response = client.get(f"/api/puestos/{puesto.id}/")

    assert response.status_code == 200
    assert response.json()["titulo"] == "Desarrollador Backend"


@pytest.mark.django_db
def test_anonymous_cannot_create_puesto():
    client = APIClient()
    response = client.post(
        "/api/puestos/",
        {"titulo": "Test", "descripcion": "Test", "requisitos": "Test"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_postulante_cannot_create_puesto(postulante):
    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.post(
        "/api/puestos/",
        {"titulo": "Test", "descripcion": "Test", "requisitos": "Test"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_reclutador_can_create_puesto_and_gets_set_as_owner(reclutador):
    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.post(
        "/api/puestos/",
        {"titulo": "QA Engineer", "descripcion": "...", "requisitos": "..."},
        format="json",
    )

    assert response.status_code == 201
    puesto = Puesto.objects.get(id=response.json()["id"])
    assert puesto.creado_por == reclutador


@pytest.mark.django_db
def test_other_reclutador_cannot_edit_someone_elses_puesto(puesto, otro_reclutador):
    client = APIClient()
    client.force_authenticate(user=otro_reclutador)
    response = client.patch(f"/api/puestos/{puesto.id}/", {"titulo": "Hackeado"}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_reclutador_can_edit_their_own_puesto(puesto, reclutador):
    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.patch(f"/api/puestos/{puesto.id}/", {"titulo": "Actualizado"}, format="json")

    assert response.status_code == 200
    puesto.refresh_from_db()
    assert puesto.titulo == "Actualizado"
