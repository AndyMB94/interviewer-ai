import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.accounts.models import ApplicantProfile


@pytest.mark.django_db
def test_applicant_profile_belongs_to_user():
    user = User.objects.create_user("andy", password="testpass123")
    profile = ApplicantProfile.objects.create(user=user, nacionalidad="Peruana")

    assert profile.user == user
    assert user.applicant_profile == profile


@pytest.mark.django_db
def test_two_blank_document_numbers_do_not_collide():
    user1 = User.objects.create_user("user1", password="testpass123")
    user2 = User.objects.create_user("user2", password="testpass123")

    ApplicantProfile.objects.create(user=user1, tipo_documento=ApplicantProfile.TipoDocumento.DNI)
    ApplicantProfile.objects.create(user=user2, tipo_documento=ApplicantProfile.TipoDocumento.DNI)


@pytest.mark.django_db
def test_same_document_type_and_number_collide():
    user1 = User.objects.create_user("user1", password="testpass123")
    user2 = User.objects.create_user("user2", password="testpass123")

    ApplicantProfile.objects.create(
        user=user1, tipo_documento=ApplicantProfile.TipoDocumento.DNI, numero_documento="12345678"
    )

    with pytest.raises(IntegrityError):
        ApplicantProfile.objects.create(
            user=user2, tipo_documento=ApplicantProfile.TipoDocumento.DNI, numero_documento="12345678"
        )
