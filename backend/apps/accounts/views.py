import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.services import ubigeo_service


def _set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.JWT_AUTH_COOKIE,
        value=refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.JWT_AUTH_COOKIE_SECURE,
        samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        path=settings.JWT_AUTH_COOKIE_PATH,
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    """Login: devuelve el access token en el body, y el refresh token en una cookie httpOnly."""

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            refresh_token = response.data.pop("refresh")
            _set_refresh_cookie(response, refresh_token)
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    """Renueva el access token leyendo el refresh token de la cookie, no del body."""

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
        if refresh_token is None:
            return Response({"detail": "Refresh token cookie missing."}, status=401)

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        data = dict(serializer.validated_data)
        new_refresh_token = data.pop("refresh", None)

        response = Response(data, status=200)
        if new_refresh_token:
            _set_refresh_cookie(response, new_refresh_token)
        return response


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """Invalida el refresh token (blacklist) y borra la cookie. Funciona aunque el access token ya haya vencido."""
    refresh_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except (TokenError, AttributeError):
            pass

    response = Response(status=205)
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path=settings.JWT_AUTH_COOKIE_PATH)
    return response


@api_view(["GET"])
@permission_classes([AllowAny])
def ubigeo_departamentos(request):
    try:
        return Response(ubigeo_service.get_departamentos())
    except requests.RequestException:
        return Response({"detail": "No se pudo obtener la lista de ubigeos."}, status=503)


@api_view(["GET"])
@permission_classes([AllowAny])
def ubigeo_provincias(request):
    departamento = request.query_params.get("departamento")
    if not departamento:
        return Response({"detail": "Falta el parámetro 'departamento'."}, status=400)
    try:
        return Response(ubigeo_service.get_provincias(departamento))
    except requests.RequestException:
        return Response({"detail": "No se pudo obtener la lista de ubigeos."}, status=503)


@api_view(["GET"])
@permission_classes([AllowAny])
def ubigeo_distritos(request):
    departamento = request.query_params.get("departamento")
    provincia = request.query_params.get("provincia")
    if not departamento or not provincia:
        return Response({"detail": "Faltan los parámetros 'departamento' y 'provincia'."}, status=400)
    try:
        return Response(ubigeo_service.get_distritos(departamento, provincia))
    except requests.RequestException:
        return Response({"detail": "No se pudo obtener la lista de ubigeos."}, status=503)
