import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.interviews.models import Interview
from apps.recruiting.models import Postulacion, Puesto
from apps.recruiting.services.postulacion_lookup import (
    get_postulaciones_aprobadas_pendientes,
    get_ultima_postulacion_aprobada,
)


@pytest.fixture
def puesto(db):
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    return Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )


@pytest.fixture
def otro_puesto(puesto):
    # Puesto distinto para simular a la misma persona postulando a más de un puesto con el mismo
    # email -- desde Infra Fase 6 un email no puede postular dos veces al MISMO puesto.
    return Puesto.objects.create(
        titulo="Dev Frontend", descripcion="...", requisitos="...", creado_por=puesto.creado_por
    )


def _fake_pdf():
    return SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf")


@pytest.mark.django_db
def test_returns_the_most_recent_aprobada_postulacion(puesto, otro_puesto):
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    mas_reciente = Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )

    resultado = get_ultima_postulacion_aprobada("andy@example.com")

    assert resultado.id == mas_reciente.id


@pytest.mark.django_db
def test_ignores_postulaciones_pendientes_or_rechazadas(puesto):
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.RECHAZADO,
    )

    assert get_ultima_postulacion_aprobada("andy@example.com") is None


@pytest.mark.django_db
def test_returns_none_when_no_match():
    assert get_ultima_postulacion_aprobada("nadie@example.com") is None


@pytest.mark.django_db
def test_pendientes_excludes_postulaciones_that_already_have_an_interview(puesto, otro_puesto):
    con_entrevista = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    Interview.objects.create(postulacion=con_entrevista)
    sin_entrevista = Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )

    resultado = get_postulaciones_aprobadas_pendientes("andy@example.com")

    assert list(resultado) == [sin_entrevista]


@pytest.mark.django_db
def test_pendientes_excludes_pendientes_y_rechazadas(puesto, otro_puesto):
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.PENDIENTE,
    )
    Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.RECHAZADO,
    )

    assert list(get_postulaciones_aprobadas_pendientes("andy@example.com")) == []


@pytest.mark.django_db
def test_pendientes_can_return_more_than_one(puesto, otro_puesto):
    p1 = Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    p2 = Postulacion.objects.create(
        puesto=otro_puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )

    resultado = list(get_postulaciones_aprobadas_pendientes("andy@example.com"))

    assert set(p.id for p in resultado) == {p1.id, p2.id}
