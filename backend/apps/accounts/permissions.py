from rest_framework.permissions import BasePermission


class IsInGroup(BasePermission):
    group_name = None

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name=self.group_name).exists()
        )


class IsAdministrador(IsInGroup):
    group_name = "Administrador"


class IsReclutador(IsInGroup):
    group_name = "Reclutador"


class IsPostulante(IsInGroup):
    group_name = "Postulante"
