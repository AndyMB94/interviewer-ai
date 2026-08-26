import secrets

from django.conf import settings
from rest_framework.permissions import BasePermission


class IsGateway(BasePermission):
    """Solo el ws-gateway puede llamar a estos endpoints -- son llamadas de servidor a servidor,
    nunca traen un JWT de usuario (Infra Fase 7). Se valida con un secreto compartido en vez de
    JWT porque el gateway no es un usuario, es el propio backend hablando con otro proceso."""

    def has_permission(self, request, view):
        secret = request.headers.get("X-Gateway-Secret", "")
        return secrets.compare_digest(secret, settings.GATEWAY_SHARED_SECRET)


class IsOwnerReclutadorOfInterview(BasePermission):
    """Solo el Reclutador dueño del puesto de la postulación conectada a esta
    entrevista puede verla. Una entrevista sin postulación (demo anónima) no
    le pertenece a ningún reclutador."""

    def has_object_permission(self, request, view, obj):
        if obj.postulacion is None:
            return False
        return obj.postulacion.puesto.creado_por_id == request.user.id
