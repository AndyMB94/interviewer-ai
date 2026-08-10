from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.permissions import IsReclutador


class IsOwnerReclutadorOrReadOnly(BasePermission):
    """Cualquiera puede leer (listar/ver un puesto). Solo un Reclutador puede crear,
    y solo el Reclutador que lo creó puede editar/borrar ese puesto puntual."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsReclutador().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.creado_por_id == request.user.id
