from rest_framework.permissions import BasePermission


class IsOwnerReclutadorOfInterview(BasePermission):
    """Solo el Reclutador dueño del puesto de la postulación conectada a esta
    entrevista puede verla. Una entrevista sin postulación (demo anónima) no
    le pertenece a ningún reclutador."""

    def has_object_permission(self, request, view, obj):
        if obj.postulacion is None:
            return False
        return obj.postulacion.puesto.creado_por_id == request.user.id
