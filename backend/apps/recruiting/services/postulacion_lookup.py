from django.db.models import QuerySet

from apps.recruiting.models import Postulacion


def get_ultima_postulacion_aprobada(email: str) -> Postulacion | None:
    return (
        Postulacion.objects.filter(email=email, estado=Postulacion.Estado.APROBADO)
        .select_related("puesto")
        .order_by("-created_at")
        .first()
    )


def get_postulaciones_aprobadas_pendientes(email: str) -> QuerySet[Postulacion]:
    return (
        Postulacion.objects.filter(email=email, estado=Postulacion.Estado.APROBADO, interviews__isnull=True)
        .select_related("puesto")
        .order_by("-created_at")
    )
