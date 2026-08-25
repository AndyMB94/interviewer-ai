import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_anon_requests_get_throttled_after_the_configured_rate():
    # No se usa override_settings: DRF "hornea" throttle_classes como atributo de clase al
    # importar el módulo, así que un override en caliente no lo actualiza -- se prueba contra
    # el límite real configurado (60/minuto) pegándole las veces que hacen falta.
    cache.clear()
    client = APIClient()
    try:
        for _ in range(60):
            assert client.get("/api/categorias/").status_code == 200
        assert client.get("/api/categorias/").status_code == 429
    finally:
        cache.clear()
