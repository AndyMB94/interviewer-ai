from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.interviews.models import Interview
from apps.recruiting.models import Categoria, Postulacion, Puesto
from apps.recruiting.pagination import StandardResultsPagination
from apps.recruiting.permissions import CanManagePostulacion, IsOwnerReclutadorOrReadOnly
from apps.recruiting.serializers import CategoriaSerializer, PostulacionSerializer, PuestoSerializer
from apps.recruiting.services.postulacion_lookup import get_postulaciones_aprobadas_pendientes
from apps.recruiting.tasks import screen_postulacion_task


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]


class PuestoViewSet(viewsets.ModelViewSet):
    serializer_class = PuestoSerializer
    permission_classes = [IsOwnerReclutadorOrReadOnly]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        queryset = Puesto.objects.select_related("categoria").annotate(
            postulaciones_count=Count("postulaciones"),
            preseleccionados=Count(
                "postulaciones__interviews",
                filter=Q(postulaciones__interviews__decision=Interview.Decision.AVANZA),
            ),
        )
        es_mias = self.request.query_params.get("mias") == "true"
        if es_mias:
            if not self.request.user.is_authenticated:
                return Puesto.objects.none()
            queryset = queryset.filter(creado_por=self.request.user)
        categoria_id = self.request.query_params.get("categoria")
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if es_mias:
            # Búsqueda y filtro de estado (Backend 9.13) solo tienen sentido en "Mis puestos": el
            # listado público (Fase 10.15, ya no filtra por estado) no tiene UI de búsqueda.
            search = self.request.query_params.get("search")
            if search:
                queryset = queryset.filter(titulo__icontains=search)
            estado = self.request.query_params.get("estado")
            if estado:
                queryset = queryset.filter(estado=estado)
        # order_by explícito: el annotate() con Count() de arriba hace que Django pierda el
        # ordenamiento implícito de Meta.ordering, y sin orden estable la paginación puede dar
        # resultados inconsistentes entre páginas (filas repetidas o salteadas).
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class PostulacionViewSet(viewsets.ModelViewSet):
    serializer_class = PostulacionSerializer
    permission_classes = [CanManagePostulacion]
    pagination_class = StandardResultsPagination
    http_method_names = ["get", "post", "head", "options"]  # sin update/destroy por ahora

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Postulacion.objects.none()
        queryset = (
            Postulacion.objects.filter(puesto__creado_por=self.request.user)
            .select_related("puesto")
            .prefetch_related("interviews")
        )
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(email__icontains=search))
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mis_postulaciones(request):
    """Fase 12.1: a diferencia de `mi_postulacion` (solo aprobadas y sin entrevistar, pensado
    para el selector de puesto), esto trae TODAS las postulaciones del candidato para el panel
    de "mis postulaciones" -- pendientes, rechazadas, aprobadas, ya entrevistadas o no. Diccionario
    propio, igual que el de arriba: nunca expone `resultado_filtro` ni `Interview.decision`, el
    candidato no debe verlos (Fase 9.10/P.4, docs/DECISIONS.md)."""
    postulaciones = (
        Postulacion.objects.filter(email=request.user.email)
        .select_related("puesto")
        .prefetch_related("interviews")
        .order_by("-created_at")
    )

    data = []
    for postulacion in postulaciones:
        interview = postulacion.interviews.first()
        data.append(
            {
                "id": postulacion.id,
                "puesto": {"id": postulacion.puesto.id, "titulo": postulacion.puesto.titulo},
                "estado": postulacion.estado,
                "created_at": postulacion.created_at,
                "fecha_limite_entrevista": postulacion.fecha_limite_entrevista,
                "entrevista_vencida": postulacion.entrevista_vencida,
                "tiene_entrevista": interview is not None,
                "entrevista_finalizada": interview is not None
                and interview.status == Interview.Status.FINISHED,
            }
        )

    return Response(data)
