from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.services import ubigeo_service

SAMPLE_TREE = {
    "LIMA": {
        "LIMA": {
            "LIMA": {"ubigeo": "150101", "id": 1},
            "MIRAFLORES": {"ubigeo": "150122", "id": 2},
        }
    },
    "CALLAO": {
        "CALLAO": {
            "CALLAO": {"ubigeo": "070101", "id": 3},
        }
    },
}


@pytest.fixture(autouse=True)
def clear_ubigeo_cache():
    cache.clear()
    yield
    cache.clear()


def _mock_response():
    response = MagicMock()
    response.json.return_value = SAMPLE_TREE
    response.raise_for_status.return_value = None
    return response


@patch("apps.accounts.services.ubigeo_service.requests.get")
def test_get_departamentos_returns_sorted_top_level_keys(mock_get):
    mock_get.return_value = _mock_response()

    assert ubigeo_service.get_departamentos() == ["CALLAO", "LIMA"]


@patch("apps.accounts.services.ubigeo_service.requests.get")
def test_get_distritos_returns_names_with_ubigeo_codes(mock_get):
    mock_get.return_value = _mock_response()

    distritos = ubigeo_service.get_distritos("LIMA", "LIMA")

    assert {"distrito": "LIMA", "ubigeo": "150101"} in distritos
    assert {"distrito": "MIRAFLORES", "ubigeo": "150122"} in distritos


@patch("apps.accounts.services.ubigeo_service.requests.get")
def test_second_call_uses_cache_not_a_new_request(mock_get):
    mock_get.return_value = _mock_response()

    ubigeo_service.get_departamentos()
    ubigeo_service.get_departamentos()

    assert mock_get.call_count == 1


@pytest.mark.django_db
@patch("apps.accounts.services.ubigeo_service.requests.get")
def test_departamentos_endpoint(mock_get):
    mock_get.return_value = _mock_response()

    response = APIClient().get("/api/auth/ubigeo/departamentos/")

    assert response.status_code == 200
    assert response.json() == ["CALLAO", "LIMA"]


@pytest.mark.django_db
@patch("apps.accounts.services.ubigeo_service.requests.get")
def test_distritos_endpoint_requires_departamento_and_provincia(mock_get):
    mock_get.return_value = _mock_response()

    response = APIClient().get("/api/auth/ubigeo/distritos/")

    assert response.status_code == 400
