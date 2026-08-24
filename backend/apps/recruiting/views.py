from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.interviews.models import Interview
from apps.recruiting.models import Categoria, Postulacion, Puesto
from apps.recruiting.permissions import CanManagePostulacion, IsOwnerReclutadorOrReadOnly
from apps.recruiting.serializers import CategoriaSerializer, PostulacionSerializer, PuestoSerializer
from apps.recruiting.services.postulacion_lookup import get_postulaciones_aprobadas_pendientes
from apps.recruiting.tasks import screen_postulacion_task


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class PuestoViewSet(viewsets.ModelViewSet):
    serializer_class = PuestoSerializer
    permission_classes = [IsOwnerReclutadorOrReadOnly]

    def get_queryset(self):
        queryset = Puesto.objects.select_related("categoria").annotate(
            postulaciones_count=Count("postulaciones"),
            preseleccionados=Count(
                "postulaciones__interviews",
                filter=Q(postulaciones__interviews__decision=Interview.Decision.AVANZA),
            ),
        )
        if self.request.query_params.get("mias") == "true":
            if not self.request.user.is_authenticated:
                return Puesto.objects.none()
            queryset = queryset.filter(creado_por=self.request.user)
        elif self.action == "list":
            # El listado público (grilla de ApplyPage) solo muestra puestos abiertos. El detalle
            # (retrieve) no se filtra acá — PuestoDetailPage necesita poder cargar un puesto cerrado
            # para mostrar el aviso de "ya no acepta postulaciones" (9.11.6), no un 404.
            queryset = queryset.filter(estado=Puesto.Estado.ABIERTO)
        categoria_id = self.request.query_params.get("categoria")
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class PostulacionViewSet(viewsets.ModelViewSet):
    serializer_class = PostulacionSerializer
    permission_classes = [CanManagePostulacion]
    http_method_names = ["get", "post", "head", "options"]  # sin update/destroy por ahora

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Postulacion.objects.none()
        return (
            Postulacion.objects.filter(puesto__creado_por=self.request.user)
            .select_related("puesto")
            .prefetch_related("interviews")
        )

    def perform_create(self, serializer):
        postulacion = serializer.save()
        screen_postulacion_task.delay(postulacion.id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mi_postulacion(request):
    postulaciones = get_postulaciones_aprobadas_pendientes(request.user.email)

    return Response(
        [
            {
                "id": postulacion.id,
                "nombre": postulacion.nombre,
                "puesto": {"id": postulacion.puesto.id, "titulo": postulacion.puesto.titulo},
            }
            for postulacion in postulaciones
        ]
    )
