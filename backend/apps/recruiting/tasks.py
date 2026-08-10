from celery import shared_task

from apps.recruiting.models import Postulacion
from apps.recruiting.services.cv_screening_service import extract_text_from_pdf, screen_candidate


@shared_task
def screen_postulacion_task(postulacion_id):
    postulacion = Postulacion.objects.select_related("puesto").get(pk=postulacion_id)

    postulacion.cv.open("rb")
    try:
        cv_text = extract_text_from_pdf(postulacion.cv)
    finally:
        postulacion.cv.close()

    resultado = screen_candidate(cv_text, postulacion.puesto)

    decision = resultado.get("decision")
    if decision == Postulacion.Estado.APROBADO:
        postulacion.estado = Postulacion.Estado.APROBADO
    elif decision == Postulacion.Estado.RECHAZADO:
        postulacion.estado = Postulacion.Estado.RECHAZADO
    # si la decisión no vino en un formato reconocible, se deja en "pendiente" (default del modelo)

    postulacion.resultado_filtro = resultado.get("razon", "")
    postulacion.save(update_fields=["estado", "resultado_filtro"])

    return postulacion.estado
