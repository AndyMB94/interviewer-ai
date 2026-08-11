from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.recruiting.models import Postulacion, Puesto
from apps.recruiting.permissions import CanManagePostulacion, IsOwnerReclutadorOrReadOnly
from apps.recruiting.serializers import PostulacionSerializer, PuestoSerializer
from apps.recruiting.services.postulacion_lookup import get_ultima_postulacion_aprobada
from apps.recruiting.tasks import screen_postulacion_task


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

    def perform_create(self, serializer):
        postulacion = serializer.save()
        screen_postulacion_task.delay(postulacion.id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mi_postulacion(request):
    postulacion = get_ultima_postulacion_aprobada(request.user.email)
    if postulacion is None:
        return Response({"detail": "No se encontró una postulación aprobada para este usuario."}, status=404)

    return Response(
        {
            "nombre": postulacion.nombre,
            "puesto": {"id": postulacion.puesto.id, "titulo": postulacion.puesto.titulo},
        }
    )
