from celery.result import AsyncResult
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.interviews.tasks import ask_llm_task


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
def ask(request):
    question = request.data.get("question")
    if not question:
        return Response({"error": "question is required"}, status=400)

    task = ask_llm_task.delay(question)
    return Response({"task_id": task.id}, status=202)


@api_view(["GET"])
def ask_result(request, task_id):
    result = AsyncResult(task_id)

    if not result.ready():
        return Response({"status": "pending"})

    return Response({"status": "done", "answer": result.result})