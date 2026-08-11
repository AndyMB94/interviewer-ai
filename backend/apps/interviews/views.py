import base64

from celery.result import AsyncResult
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.interviews.models import Interview, Question
from apps.interviews.tasks import ask_llm_task, synthesize_speech_task, transcribe_audio_task


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
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
        interview = Interview.objects.create(user=user)

    question = Question.objects.create(interview=interview, text=question_text)

    task = ask_llm_task.delay(question.id)
    return Response({"task_id": task.id, "interview_id": interview.id}, status=202)


@api_view(["GET"])
def ask_result(request, task_id):
    result = AsyncResult(task_id)

    if not result.ready():
        return Response({"status": "pending"})

    return Response({"status": "done", "answer": result.result})


@api_view(["POST"])
def transcribe(request):
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return Response({"error": "audio file is required"}, status=400)

    audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
    task = transcribe_audio_task.delay(audio_base64)
    return Response({"task_id": task.id}, status=202)


@api_view(["GET"])
def transcribe_result(request, task_id):
    result = AsyncResult(task_id)

    if not result.ready():
        return Response({"status": "pending"})

    return Response({"status": "done", "transcript": result.result})


@api_view(["POST"])
def speak(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "text is required"}, status=400)

    task = synthesize_speech_task.delay(text)
    return Response({"task_id": task.id}, status=202)


@api_view(["GET"])
def speak_result(request, task_id):
    result = AsyncResult(task_id)

    if not result.ready():
        return Response({"status": "pending"})

    return Response({"status": "done", "audio_url": result.result})