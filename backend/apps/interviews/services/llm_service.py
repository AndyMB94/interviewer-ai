import os

from openai import OpenAI

SYSTEM_PROMPT = (
    "Sos un entrevistador técnico de programación, evaluando a un candidato en una entrevista de trabajo por voz. "
    "Hacé preguntas técnicas relevantes, evaluá las respuestas del candidato con criterio profesional, y sé cordial pero directo. "
    "IMPORTANTE: tus respuestas se convierten a voz (texto a audio) y el candidato las escucha, no las lee. "
    "Respondé de forma breve y conversacional, como en una charla real — nunca uses títulos, viñetas, markdown ni listas numeradas. "
    "Si necesitás mencionar varios puntos, decilos en una o dos oraciones fluidas, no como un documento estructurado."
)


def ask_llm(question: str, history: list[dict] | None = None) -> str:
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=False,
    )
    return response.choices[0].message.content