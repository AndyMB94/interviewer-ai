from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import ApplicantProfile


class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantProfile
        fields = [
            "tipo_documento",
            "numero_documento",
            "nacionalidad",
            "fecha_nacimiento",
            "sexo",
            "telefono",
            "ubigeo_codigo",
            "departamento",
            "provincia",
            "distrito",
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Agrega los Groups y el email del usuario al payload del JWT — el frontend usa `groups` para
    decidir a dónde redirigir después de loguear (dashboard de reclutador vs. entrevista de
    postulante), y `email` para reconstruir la sesión en el "silent refresh" al cargar la app
    (Frontend Fase P.7), sin depender de lo que el usuario tipeó en el form. No es un mecanismo de
    autorización: cada endpoint sigue validando el rol contra la base en cada request, ver
    DECISIONS.md."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["groups"] = list(user.groups.values_list("name", flat=True))
        token["email"] = user.email
        return token
