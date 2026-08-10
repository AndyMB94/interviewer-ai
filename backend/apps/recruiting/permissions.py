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


class CanManagePostulacion(BasePermission):
    """Postular es público (sin cuenta). Ver/listar postulaciones es solo para el
    Reclutador dueño del puesto al que corresponde esa postulación."""

    def has_permission(self, request, view):
        if view.action == "create":
            return True
        return IsReclutador().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return obj.puesto.creado_por_id == request.user.id
