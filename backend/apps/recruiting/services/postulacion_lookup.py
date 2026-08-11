from apps.recruiting.models import Postulacion


def get_ultima_postulacion_aprobada(email: str) -> Postulacion | None:
    return (
        Postulacion.objects.filter(email=email, estado=Postulacion.Estado.APROBADO)
        .select_related("puesto")
        .order_by("-created_at")
        .first()
    )
