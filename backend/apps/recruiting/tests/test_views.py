import uuid
from datetime import timedelta

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.interviews.models import Interview
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
    assert len(response.json()["results"]) == 1


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
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto.id


@pytest.mark.django_db
def test_mias_filter_returns_empty_for_anonymous():
    client = APIClient()
    response = client.get("/api/puestos/?mias=true")

    assert response.status_code == 200
    assert response.json()["results"] == []


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

    data = response.json()["results"]
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
def test_mis_postulaciones_requires_authentication():
    client = APIClient()
    response = client.get("/api/postulaciones/mias/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_mis_postulaciones_includes_every_estado(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    otro_puesto = Puesto.objects.create(
        titulo="Otro puesto", descripcion="...", requisitos="...", creado_por=puesto.creado_por
    )
    tercer_puesto = Puesto.objects.create(
        titulo="Tercer puesto", descripcion="...", requisitos="...", creado_por=puesto.creado_por
    )
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.PENDIENTE,
    )
    Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.RECHAZADO,
    )
    Postulacion.objects.create(
        puesto=tercer_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
        fecha_limite_entrevista=timezone.now() + timedelta(days=2),
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mias/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    estados = {item["puesto"]["titulo"]: item["estado"] for item in data}
    assert estados == {
        puesto.titulo: Postulacion.Estado.PENDIENTE,
        "Otro puesto": Postulacion.Estado.RECHAZADO,
        "Tercer puesto": Postulacion.Estado.APROBADO,
    }
    aprobada = next(item for item in data if item["puesto"]["titulo"] == "Tercer puesto")
    assert aprobada["fecha_limite_entrevista"] is not None
    assert aprobada["entrevista_vencida"] is False
    assert aprobada["tiene_entrevista"] is False
    assert aprobada["entrevista_finalizada"] is False


@pytest.mark.django_db
def test_mis_postulaciones_never_exposes_resultado_filtro_or_decision(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    postulacion = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.RECHAZADO,
        resultado_filtro="No cumple los requisitos técnicos del puesto.",
    )
    interview = Interview.objects.create(postulacion=postulacion, status=Interview.Status.FINISHED)
    interview.decision = Interview.Decision.NO_AVANZA
    interview.save(update_fields=["decision"])

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mias/")

    assert response.status_code == 200
    raw_body = response.content.decode()
    assert "resultado_filtro" not in raw_body
    assert "No cumple los requisitos" not in raw_body
    assert "decision" not in raw_body
    assert "no_avanza" not in raw_body
    data = response.json()
    assert data[0]["tiene_entrevista"] is True
    assert data[0]["entrevista_finalizada"] is True


@pytest.mark.django_db
def test_mis_postulaciones_marks_expired_deadline(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
        fecha_limite_entrevista=timezone.now() - timedelta(days=1),
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mias/")

    assert response.status_code == 200
    assert response.json()[0]["entrevista_vencida"] is True


@pytest.mark.django_db
def test_mis_postulaciones_only_returns_the_authenticated_users_own(puesto):
    postulante = User.objects.create_user(
        "andy@example.com", email="andy@example.com", password="testpass123"
    )
    postulante.groups.add(Group.objects.get(name="Postulante"))
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Carla",
        email="carla@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/postulaciones/mias/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_anyone_can_list_categorias():
    Categoria.objects.create(nombre="Categoría de prueba")

    client = APIClient()
    response = client.get("/api/categorias/")

    assert response.status_code == 200
    # Regresión: a diferencia de Puesto/Postulacion (9.12), Categoria no lleva pagination_class a
    # propósito — su listado sigue siendo un array plano, no {count, next, previous, results}.
    assert isinstance(response.json(), list)
    nombres = [c["nombre"] for c in response.json()]
    assert "Categoría de prueba" in nombres


@pytest.mark.django_db
def test_puesto_includes_categoria_nombre_when_set(puesto):
    categoria = Categoria.objects.create(nombre="Categoría de prueba")
    puesto.categoria = categoria
    puesto.save()

    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()["results"][0]["categoria_nombre"] == "Categoría de prueba"


@pytest.mark.django_db
def test_puesto_categoria_nombre_is_null_without_categoria(puesto):
    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()["results"][0]["categoria_nombre"] is None


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
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto.id


@pytest.mark.django_db
def test_puesto_default_vacantes_is_one(puesto):
    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()["results"][0]["vacantes"] == 1


@pytest.mark.django_db
def test_creating_puesto_with_zero_vacantes_is_rejected(reclutador):
    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.post(
        "/api/puestos/",
        {"titulo": "Test", "descripcion": "Test", "requisitos": "Test", "vacantes": 0},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_public_list_includes_puestos_cerrados(reclutador):
    # Fase 10.15/Decisión 9: un puesto cerrado se sigue mostrando en el catálogo público (con
    # badge en el frontend), no desaparece del todo -- mismo criterio que LinkedIn/Indeed.
    puesto_cerrado = Puesto.objects.create(
        titulo="Puesto cerrado",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        estado=Puesto.Estado.CERRADO,
    )

    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto_cerrado.id
    assert data[0]["acepta_postulaciones"] is False


@pytest.mark.django_db
def test_mias_filter_includes_puestos_cerrados(reclutador):
    puesto_cerrado = Puesto.objects.create(
        titulo="Puesto cerrado",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        estado=Puesto.Estado.CERRADO,
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto_cerrado.id


@pytest.mark.django_db
def test_anyone_can_retrieve_a_puesto_cerrado(reclutador):
    puesto_cerrado = Puesto.objects.create(
        titulo="Puesto cerrado",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        estado=Puesto.Estado.CERRADO,
    )

    client = APIClient()
    response = client.get(f"/api/puestos/{puesto_cerrado.id}/")

    assert response.status_code == 200
    assert response.json()["estado"] == "cerrado"


def _postulacion_aprobada(puesto, email=None):
    # Email único por default (Infra Fase 6 -- un email no puede postular dos veces al mismo
    # puesto), para que este helper se pueda llamar más de una vez con el mismo puesto sin chocar.
    return Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email=email or f"andy+{uuid.uuid4().hex[:8]}@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
        estado=Postulacion.Estado.APROBADO,
    )


@pytest.mark.django_db
def test_puesto_counts_only_interviews_with_avanza_as_preseleccionados(puesto):
    postulacion_avanza = _postulacion_aprobada(puesto)
    Interview.objects.create(postulacion=postulacion_avanza, decision=Interview.Decision.AVANZA)

    postulacion_no_avanza = _postulacion_aprobada(puesto)
    Interview.objects.create(postulacion=postulacion_no_avanza, decision=Interview.Decision.NO_AVANZA)

    postulacion_pendiente = _postulacion_aprobada(puesto)
    Interview.objects.create(postulacion=postulacion_pendiente, decision=Interview.Decision.PENDIENTE)

    client = APIClient()
    response = client.get("/api/puestos/")

    assert response.json()["results"][0]["preseleccionados"] == 1


@pytest.mark.django_db
def test_puesto_list_is_paginated_with_more_than_one_page(reclutador):
    for i in range(13):
        Puesto.objects.create(
            titulo=f"Puesto {i}", descripcion="...", requisitos="...", creado_por=reclutador
        )

    client = APIClient()
    page_1 = client.get("/api/puestos/").json()
    assert page_1["count"] == 13
    assert len(page_1["results"]) == 12
    assert page_1["next"] is not None
    assert page_1["previous"] is None


@pytest.mark.django_db
def test_mias_search_filters_by_titulo_case_insensitive_and_partial(puesto, reclutador):
    Puesto.objects.create(
        titulo="Contador senior", descripcion="...", requisitos="...", creado_por=reclutador
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true&search=BACK")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto.id


@pytest.mark.django_db
def test_mias_search_without_match_returns_empty_list(puesto, reclutador):
    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true&search=inexistente")

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_mias_estado_filter(puesto, reclutador):
    Puesto.objects.create(
        titulo="Puesto cerrado",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        estado=Puesto.Estado.CERRADO,
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true&estado=cerrado")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["estado"] == "cerrado"


@pytest.mark.django_db
def test_mias_search_and_estado_combined(puesto, reclutador):
    Puesto.objects.create(
        titulo="Desarrollador Frontend",
        descripcion="...",
        requisitos="...",
        creado_por=reclutador,
        estado=Puesto.Estado.CERRADO,
    )

    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/puestos/?mias=true&search=desarrollador&estado=abierto")

    assert response.status_code == 200
    data = response.json()["results"]
    assert len(data) == 1
    assert data[0]["id"] == puesto.id


@pytest.mark.django_db
def test_search_and_estado_are_ignored_on_public_listing(puesto, reclutador):
    Puesto.objects.create(
        titulo="Contador senior", descripcion="...", requisitos="...", creado_por=reclutador
    )

    client = APIClient()
    response = client.get("/api/puestos/?search=backend")

    assert response.status_code == 200
    assert len(response.json()["results"]) == 2
