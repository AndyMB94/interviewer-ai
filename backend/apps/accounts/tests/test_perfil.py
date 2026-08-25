import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient

from apps.accounts.models import ApplicantProfile


@pytest.fixture
def postulante():
    user = User.objects.create_user("postulante1", password="testpass123")
    user.groups.add(Group.objects.get(name="Postulante"))
    return user


@pytest.fixture
def reclutador():
    user = User.objects.create_user("reclutador1", password="testpass123")
    user.groups.add(Group.objects.get(name="Reclutador"))
    return user


@pytest.mark.django_db
def test_anonymous_cannot_access_perfil():
    client = APIClient()
    response = client.get("/api/auth/perfil/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_reclutador_cannot_access_perfil(reclutador):
    client = APIClient()
    client.force_authenticate(user=reclutador)
    response = client.get("/api/auth/perfil/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_postulante_gets_an_empty_profile_created_on_first_access(postulante):
    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.get("/api/auth/perfil/")

    assert response.status_code == 200
    assert response.json()["telefono"] == ""
    assert ApplicantProfile.objects.filter(user=postulante).exists()


@pytest.mark.django_db
def test_postulante_can_update_their_own_profile(postulante):
    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.patch(
        "/api/auth/perfil/",
        {
            "tipo_documento": "dni",
            "numero_documento": "12345678",
            "telefono": "999888777",
            "departamento": "Lima",
            "provincia": "Lima",
            "distrito": "Miraflores",
        },
        format="json",
    )

    assert response.status_code == 200
    profile = ApplicantProfile.objects.get(user=postulante)
    assert profile.numero_documento == "12345678"
    assert profile.distrito == "Miraflores"


@pytest.mark.django_db
def test_updating_with_a_duplicate_document_number_returns_400_not_500(postulante):
    otro = User.objects.create_user("postulante2", password="testpass123")
    ApplicantProfile.objects.create(
        user=otro, tipo_documento=ApplicantProfile.TipoDocumento.DNI, numero_documento="12345678"
    )

    client = APIClient()
    client.force_authenticate(user=postulante)
    response = client.patch(
        "/api/auth/perfil/",
        {"tipo_documento": "dni", "numero_documento": "12345678"},
        format="json",
    )

    assert response.status_code == 400
