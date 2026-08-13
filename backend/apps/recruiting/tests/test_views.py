import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.recruiting.models import Categoria, Postulacion, Puesto


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


@pytest.mark.django_db
def test_mias_filter_returns_only_the_reclutador_own_puestos(puesto, otro_reclutador, reclutador):
    Puesto.objects.create(
        titulo="QA Engineer", descripcion="...", requisitos="...", creado_por=otro_reclutador
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == puesto.id


@pytest.mark.django_db
def test_mias_filter_returns_empty_for_anonymous():
    client = APIClient()
    response = client.get("/api/puestos/?mias=true")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_puesto_list_includes_postulaciones_count(puesto):
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
    )

    client = APIClient()
    response = client.get("/api/puestos/")

    data = response.json()
    assert data[0]["postulaciones_count"] == 1


@pytest.mark.django_db
def test_mi_postulacion_requires_authentication():
    client = APIClient()
    response = client.get("/api/postulaciones/mia/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_mi_postulacion_returns_empty_list_without_a_matching_aprobada(postulante):
    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mia/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_mi_postulacion_returns_nombre_and_puesto(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mia/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Andy Mallcco"
    assert data[0]["puesto"]["titulo"] == puesto.titulo


@pytest.mark.django_db
def test_mi_postulacion_returns_more_than_one_when_pending(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    otro_puesto = Puesto.objects.create(
        titulo="Otro puesto", descripcion="...", requisitos="...", creado_por=puesto.creado_por
    )
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )
    Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mia/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.django_db
def test_anyone_can_list_categorias():
    Categoria.objects.create(nombre="Categoría de prueba")

    client = APIClient()
    response = client.get("/api/categorias/")

    assert response.status_code == 200
    nombres = [c["nombre"] for c in response.json()]
    assert "Categoría de prueba" in nombres


@pytest.mark.django_db
def test_puesto_includes_categoria_nombre_when_set(puesto):
    categoria = Categoria.objects.create(nombre="Categoría de prueba")
    puesto.categoria = categoria
    puesto.save()

    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()[0]["categoria_nombre"] == "Categoría de prueba"


@pytest.mark.django_db
def test_puesto_categoria_nombre_is_null_without_categoria(puesto):
    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()[0]["categoria_nombre"] is None


@pytest.mark.django_db
def test_puestos_filter_by_categoria(puesto, reclutador):
    categoria_a = Categoria.objects.create(nombre="Categoría A de prueba")
    categoria_b = Categoria.objects.create(nombre="Categoría B de prueba")
    puesto.categoria = categoria_a
    puesto.save()
    Puesto.objects.create(
        titulo="Abogado corporativo",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        categoria=categoria_b,
    )

    client = APIClient()
    response = client.get(f"/api/puestos/?categoria={categoria_a.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == puesto.id
