from rest_framework import viewsets

from apps.recruiting.models import Puesto
from apps.recruiting.permissions import IsOwnerReclutadorOrReadOnly
from apps.recruiting.serializers import PuestoSerializer


class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    permission_classes = [IsOwnerReclutadorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
