from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Agrega los Groups del usuario al payload del JWT — el frontend lo usa para decidir a dónde
    redirigir después de loguear (dashboard de reclutador vs. entrevista de postulante). No es un
    mecanismo de autorización: cada endpoint sigue validando el rol contra la base en cada request,
    ver DECISIONS.md."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["groups"] = list(user.groups.values_list("name", flat=True))
        return token
