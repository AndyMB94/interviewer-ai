import pytest

from apps.recruiting.models import Categoria


@pytest.mark.django_db
def test_migration_seeds_the_curated_categoria_set():
    nombres = set(Categoria.objects.values_list("nombre", flat=True))

    assert {
        "Tecnología / Sistemas",
        "Recursos Humanos",
        "Ventas",
        "Servicios Generales / Limpieza / Seguridad",
    }.issubset(nombres)
