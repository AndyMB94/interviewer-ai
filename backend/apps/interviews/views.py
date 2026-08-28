import base64
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.interviews.models import Interview, Question
from apps.interviews.permissions import IsGateway, IsOwnerReclutadorOfInterview
from apps.interviews.tasks import ask_llm_task, synthesize_speech_task, transcribe_audio_task
from apps.recruiting.models import Postulacion

# Fase 10.5/10.9: duración máxima de una entrevista, calculada contra Interview.created_at --
# nunca confiando en el cronómetro del frontend, que es solo para que se sienta transparente.
DURACION_MAXIMA_ENTREVISTA = timedelta(minutes=30)
MENSAJE_TIEMPO_AGOTADO = (
    "Se acabó el tiempo disponible para esta entrevista. Gracias por su participación — "
    "sus respuestas ya quedaron registradas."
)


def finalizar_si_vencida(interview):
    """Fase 10.11: mismo chequeo perezoso de siempre, evaluado en cualquier lugar que lea o
    toque la entrevista -- no solo cuando llega un mensaje nuevo (`ask`). Cubre el caso de
    alguien que cierra el navegador a los 30 minutos y nunca vuelve: sin esto, esa entrevista
    quedaría "en progreso" para siempre, tanto para el candidato como en el panel del reclutador."""
    if (
        interview.status == Interview.Status.IN_PROGRESS
        and timezone.now() - interview.created_at > DURACION_MAXIMA_ENTREVISTA
    ):
        interview.status = Interview.Status.FINISHED
        interview.save(update_fields=["status"])
        return True
    return False


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsGateway])
def ask(request):
    question_text = request.data.get("question")
    if not question_text:
        return Response({"error": "question is required"}, status=400)

    interview_id = request.data.get("interview_id")
    if interview_id:
        interview = Interview.objects.filter(pk=interview_id).first()
        if interview is None:
            return Response({"error": "interview not found"}, status=404)
    else:
        user = request.user if request.user.is_authenticated else None
        postulacion_id = request.data.get("postulacion_id")

        postulacion = None
        if postulacion_id:
            if user is None:
                return Response({"error": "authentication required to select a postulacion"}, status=401)
            postulacion = Postulacion.objects.filter(
                pk=postulacion_id, email=user.email, estado=Postulacion.Estado.APROBADO
            ).first()
            if postulacion is None:
                return Response({"error": "postulacion not found"}, status=404)
            if postulacion.interviews.exists():
                return Response({"error": "this postulacion already has an interview"}, status=409)
            if postulacion.entrevista_vencida:
                return Response(
                    {"error": "the deadline to start this interview has passed"}, status=410
                )

        interview = Interview.objects.create(user=user, postulacion=postulacion)

    if finalizar_si_vencida(interview):
        return Response(
            {"timed_out": True, "interview_id": interview.id, "message": MENSAJE_TIEMPO_AGOTADO}
        )

    question = Question.objects.create(interview=interview, text=question_text)

    task = ask_llm_task.delay(question.id)
    return Response(
        {"task_id": task.id, "interview_id": interview.id, "created_at": interview.created_at},
        status=202,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def interview_en_curso(request):
    """Fase 10.4: detecta si el postulante autenticado ya tiene una entrevista sin terminar
    (ej. cerró el navegador a medio camino) para poder retomarla con su historial real -- sin
    esto, el intento de crear una entrevista nueva choca contra la que ya existe (409 en `ask`)."""
    interview = (
        Interview.objects.filter(user=request.user, status=Interview.Status.IN_PROGRESS)
        .select_related("postulacion__puesto")
        .order_by("-created_at")
        .first()
    )
    if interview is None:
        return Response(status=204)

    if finalizar_si_vencida(interview):
        return Response(status=204)

    questions = [
        {
            "question": question.text,
            "created_at": question.created_at,
            "answer": question.answer.text if hasattr(question, "answer") else None,
            "answered_at": question.answer.created_at if hasattr(question, "answer") else None,
        }
        for question in interview.questions.select_related("answer").order_by("created_at")
    ]

    return Response(
        {
            "interview_id": interview.id,
            "postulacion_id": interview.postulacion_id,
            "puesto_titulo": interview.postulacion.puesto.titulo if interview.postulacion else None,
            "created_at": interview.created_at,
            "questions": questions,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def interview_detail(request, interview_id):
    interview = get_object_or_404(
        Interview.objects.select_related("postulacion__puesto"), pk=interview_id
    )
    if not IsOwnerReclutadorOfInterview().has_object_permission(request, None, interview):
        return Response({"detail": "No tiene permiso para ver esta entrevista."}, status=403)

    finalizar_si_vencida(interview)

    questions = [
        {
            "question": question.text,
            "created_at": question.created_at,
            "answer": question.answer.text if hasattr(question, "answer") else None,
            "answered_at": question.answer.created_at if hasattr(question, "answer") else None,
        }
        for question in interview.questions.select_related("answer").order_by("created_at")
    ]

    return Response(
        {
            "id": interview.id,
            "status": interview.status,
            "decision": interview.decision,
            "created_at": interview.created_at,
            "postulacion": {
                "nombre": interview.postulacion.nombre,
                "puesto_titulo": interview.postulacion.puesto.titulo,
                "estado": interview.postulacion.estado,
                "resultado_filtro": interview.postulacion.resultado_filtro,
            },
            "questions": questions,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_interview_decision(request, interview_id):
    interview = get_object_or_404(Interview.objects.select_related("postulacion__puesto"), pk=interview_id)
    if not IsOwnerReclutadorOfInterview().has_object_permission(request, None, interview):
        return Response({"detail": "No tiene permiso para modificar esta entrevista."}, status=403)

    decision = request.data.get("decision")
    if decision not in Interview.Decision.values:
        return Response({"error": "decision inválida"}, status=400)

    interview.decision = decision
    interview.save(update_fields=["decision"])
    return Response({"decision": interview.decision})


@api_view(["POST"])
@permission_classes([IsGateway])
def finish_interview(request, interview_id):
    interview = get_object_or_404(Interview, pk=interview_id)
    interview.status = Interview.Status.FINISHED
    interview.save(update_fields=["status"])
    return Response({"status": interview.status})


@api_view(["POST"])
@permission_classes([IsGateway])
def transcribe(request):
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return Response({"error": "audio file is required"}, status=400)

    audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
    task = transcribe_audio_task.delay(audio_base64)
    return Response({"task_id": task.id}, status=202)


@api_view(["POST"])
@permission_classes([IsGateway])
def speak(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "text is required"}, status=400)

    task = synthesize_speech_task.delay(text)
    return Response({"task_id": task.id}, status=202)