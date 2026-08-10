import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIRequestFactory

from apps.accounts.permissions import IsAdministrador, IsPostulante, IsReclutador


def _request_as(user):
    request = APIRequestFactory().get("/")
    request.user = user
    return request


@pytest.mark.django_db
def test_user_in_reclutador_group_passes_is_reclutador():
    user = User.objects.create_user("reclutador1", password="testpass123")
    user.groups.add(Group.objects.get(name="Reclutador"))

    assert IsReclutador().has_permission(_request_as(user), None) is True
    assert IsAdministrador().has_permission(_request_as(user), None) is False
    assert IsPostulante().has_permission(_request_as(user), None) is False


@pytest.mark.django_db
def test_user_without_groups_fails_all_role_checks():
    user = User.objects.create_user("nobody", password="testpass123")

    assert IsAdministrador().has_permission(_request_as(user), None) is False
    assert IsReclutador().has_permission(_request_as(user), None) is False
    assert IsPostulante().has_permission(_request_as(user), None) is False
