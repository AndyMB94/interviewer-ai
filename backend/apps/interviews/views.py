import os
from openai import OpenAI
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})

@api_view(["POST"])
def ask(request):
    question = request.data.get("question")
    if not question:
        return Response({"error": "question is required"}, status=400)

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": question},
        ],
        stream=False,
    )

    return Response({"answer": response.choices[0].message.content})