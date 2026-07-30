from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.interviews.services.llm_service import ask_llm


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
def ask(request):
    question = request.data.get("question")
    if not question:
        return Response({"error": "question is required"}, status=400)

    answer = ask_llm(question)
    return Response({"answer": answer})