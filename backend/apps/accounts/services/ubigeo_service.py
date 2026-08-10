import requests
from django.core.cache import cache

UBIGEO_SOURCE_URL = "https://free.e-api.net.pe/ubigeos.json"
CACHE_KEY = "ubigeo_tree"
CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 30 días: el dato prácticamente no cambia


def _fetch_tree() -> dict:
    response = requests.get(UBIGEO_SOURCE_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def get_tree() -> dict:
    tree = cache.get(CACHE_KEY)
    if tree is None:
        tree = _fetch_tree()
        cache.set(CACHE_KEY, tree, CACHE_TIMEOUT)
    return tree


def get_departamentos() -> list[str]:
    return sorted(get_tree().keys())


def get_provincias(departamento: str) -> list[str]:
    provincias = get_tree().get(departamento, {})
    return sorted(provincias.keys())


def get_distritos(departamento: str, provincia: str) -> list[dict]:
    distritos = get_tree().get(departamento, {}).get(provincia, {})
    return [
        {"distrito": nombre, "ubigeo": datos["ubigeo"]}
        for nombre, datos in sorted(distritos.items())
    ]
