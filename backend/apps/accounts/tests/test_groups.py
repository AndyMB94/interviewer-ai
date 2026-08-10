import pytest
from django.contrib.auth.models import Group


@pytest.mark.django_db
def test_migration_creates_the_three_roles():
    names = set(Group.objects.values_list("name", flat=True))

    assert {"Administrador", "Reclutador", "Postulante"}.issubset(names)
