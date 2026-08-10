from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recruiting.models import Postulacion, Puesto
from apps.recruiting.tasks import screen_postulacion_task


@pytest.fixture
def postulacion(db):
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    puesto = Puesto.objects.create(
        titulo="Dev Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )
    return Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy",
        email="andy@example.com",
        cv=SimpleUploadedFile("cv.pdf", b"contenido", content_type="application/pdf"),
    )


@pytest.mark.django_db
@patch("apps.recruiting.tasks.extract_text_from_pdf", return_value="texto extraído")
@patch("apps.recruiting.tasks.screen_candidate")
def test_task_marks_postulacion_as_aprobado(mock_screen, mock_extract, postulacion):
    mock_screen.return_value = {"decision": "aprobado", "razon": "Buen fit."}

    screen_postulacion_task(postulacion.id)

    postulacion.refresh_from_db()
    assert postulacion.estado == Postulacion.Estado.APROBADO
    assert postulacion.resultado_filtro == "Buen fit."


@pytest.mark.django_db
@patch("apps.recruiting.tasks.extract_text_from_pdf", return_value="texto extraído")
@patch("apps.recruiting.tasks.screen_candidate")
def test_task_marks_postulacion_as_rechazado(mock_screen, mock_extract, postulacion):
    mock_screen.return_value = {"decision": "rechazado", "razon": "No cumple los requisitos."}

    screen_postulacion_task(postulacion.id)

    postulacion.refresh_from_db()
    assert postulacion.estado == Postulacion.Estado.RECHAZADO


@pytest.mark.django_db
@patch("apps.recruiting.tasks.extract_text_from_pdf", return_value="texto extraído")
@patch("apps.recruiting.tasks.screen_candidate")
def test_task_leaves_pendiente_if_decision_is_unrecognizable(mock_screen, mock_extract, postulacion):
    mock_screen.return_value = {"decision": None, "razon": "No se pudo interpretar."}

    screen_postulacion_task(postulacion.id)

    postulacion.refresh_from_db()
    assert postulacion.estado == Postulacion.Estado.PENDIENTE
