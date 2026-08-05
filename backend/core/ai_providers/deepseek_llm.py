import os

from openai import OpenAI

from core.ai_providers.base import LLMProvider

SYSTEM_PROMPT = (
    "Usted es un entrevistador técnico de programación, evaluando a un candidato en una entrevista de trabajo por voz. "
    "Haga preguntas técnicas relevantes, evalúe las respuestas del candidato con criterio profesional, y sea cordial pero directo. "
    "IMPORTANTE: sus respuestas se convierten a voz (texto a audio) y el candidato las escucha, no las lee. "
    "Responda de forma breve y conversacional, como en una charla real — nunca use títulos, viñetas, markdown ni listas numeradas. "
    "Si necesita mencionar varios puntos, dígalos en una o dos oraciones fluidas, no como un documento estructurado."
)


class DeepSeekLLM(LLMProvider):
    def ask(self, question: str, history: list[dict] | None = None) -> str:
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
