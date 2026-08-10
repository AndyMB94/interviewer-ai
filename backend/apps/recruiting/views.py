from rest_framework import viewsets

from apps.recruiting.models import Postulacion, Puesto
from apps.recruiting.permissions import CanManagePostulacion, IsOwnerReclutadorOrReadOnly
from apps.recruiting.serializers import PostulacionSerializer, PuestoSerializer


class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    permission_classes = [IsOwnerReclutadorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class PostulacionViewSet(viewsets.ModelViewSet):
    serializer_class = PostulacionSerializer
    permission_classes = [CanManagePostulacion]
    http_method_names = ["get", "post", "head", "options"]  # sin update/destroy por ahora

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Postulacion.objects.none()
        return Postulacion.objects.filter(puesto__creado_por=self.request.user)
