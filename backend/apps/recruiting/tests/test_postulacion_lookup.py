import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recruiting.models import Postulacion, Puesto
from apps.recruiting.services.postulacion_lookup import get_ultima_postulacion_aprobada


@pytest.fixture
def puesto(db):
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    return Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )


def _fake_pdf():
    return SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf")


@pytest.mark.django_db
def test_returns_the_most_recent_aprobada_postulacion(puesto):
    Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=_fake_pdf(),
        estado=Postulacion.Estado.APROBADO,
    )
    mas_reciente = Postulacion.objects.create(
        puesto=puesto,
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
