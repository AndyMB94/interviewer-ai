import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from django.conf import settings


@pytest.fixture
def user():
    return User.objects.create_user("andy", password="testpass123")


@pytest.mark.django_db
def test_login_returns_access_and_sets_httponly_cookie(user):
    client = APIClient()
    response = client.post(
        "/api/auth/login/", {"username": "andy", "password": "testpass123"}, format="json"
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data

    cookie = response.cookies[settings.JWT_AUTH_COOKIE]
    assert cookie["httponly"] is True


@pytest.mark.django_db
def test_login_with_wrong_password_fails(user):
    client = APIClient()
    response = client.post(
        "/api/auth/login/", {"username": "andy", "password": "wrong"}, format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_with_valid_cookie_issues_new_access(user):
    client = APIClient()
    client.post("/api/auth/login/", {"username": "andy", "password": "testpass123"}, format="json")

    response = client.post("/api/auth/token/refresh/")

    assert response.status_code == 200
    assert "access" in response.data
    assert settings.JWT_AUTH_COOKIE in response.cookies


@pytest.mark.django_db
def test_refresh_without_cookie_fails():
    client = APIClient()
    response = client.post("/api/auth/token/refresh/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_logout_clears_cookie_and_blacklists_refresh(user):
    client = APIClient()
    client.post("/api/auth/login/", {"username": "andy", "password": "testpass123"}, format="json")
    old_refresh_token = client.cookies[settings.JWT_AUTH_COOKIE].value

    logout_response = client.post("/api/auth/logout/")
    assert logout_response.status_code == 205
    assert client.cookies[settings.JWT_AUTH_COOKIE].value == ""

    # forzamos de nuevo el token viejo en la cookie (simula a alguien reusando un token robado/expirado)
    client.cookies[settings.JWT_AUTH_COOKIE] = old_refresh_token
    refresh_response = client.post("/api/auth/token/refresh/")
    assert refresh_response.status_code == 401


@pytest.mark.django_db
def test_logout_works_even_with_an_active_django_admin_session(user):
    """Regresión: si el navegador también tiene una sesión de /admin/ activa (cookie de sesión de
    Django), SessionAuthentication la detectaba y exigía CSRF, que el frontend nunca manda —
    daba 403. Se sacó SessionAuthentication de REST_FRAMEWORK (la API es JWT puro, no sesión)."""
    client = APIClient()
    client.force_login(user)  # simula tener una sesión de Django activa en el navegador

    response = client.post("/api/auth/logout/")

    assert response.status_code == 205
