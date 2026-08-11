import pytest
from django.contrib.auth.models import Group, User
from django.core import mail

from apps.accounts.models import ApplicantProfile
from apps.accounts.services.account_provisioning import procesar_aprobacion, provision_applicant_account
from apps.recruiting.models import Postulacion, Puesto


@pytest.fixture
def puesto(db):
    reclutador = User.objects.create_user("reclutador1", password="testpass123")
    reclutador.groups.add(Group.objects.get(name="Reclutador"))
    return Puesto.objects.create(
        titulo="Desarrollador Backend", descripcion="...", requisitos="...", creado_por=reclutador
    )


@pytest.fixture
def postulacion(puesto):
    return Postulacion.objects.create(
        puesto=puesto,
        nombre="Andy Mallcco",
        email="andy@example.com",
        cv="cvs/cv.pdf",
        estado=Postulacion.Estado.APROBADO,
    )


@pytest.mark.django_db
def test_provision_creates_new_user_in_postulante_group(postulacion):
    user, password_temporal = provision_applicant_account(postulacion)

    assert user.username == "andy@example.com"
    assert user.groups.filter(name="Postulante").exists()
    assert ApplicantProfile.objects.filter(user=user).exists()
    assert user.check_password(password_temporal)


@pytest.mark.django_db
def test_provision_resets_password_for_existing_user(postulacion):
    user, primera_password = provision_applicant_account(postulacion)
    user, segunda_password = provision_applicant_account(postulacion)

    assert User.objects.filter(username="andy@example.com").count() == 1
    assert primera_password != segunda_password
    assert user.check_password(segunda_password)
    assert not user.check_password(primera_password)


@pytest.mark.django_db
def test_procesar_aprobacion_sends_credentials_email(postulacion):
    procesar_aprobacion(postulacion)

    assert len(mail.outbox) == 1
    email_enviado = mail.outbox[0]
    assert email_enviado.to == ["andy@example.com"]
    assert "Desarrollador Backend" in email_enviado.subject
