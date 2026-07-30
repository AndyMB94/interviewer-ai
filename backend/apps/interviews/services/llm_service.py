import os

from openai import OpenAI


def ask_llm(question: str, history: list[dict] | None = None) -> str:
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    messages = [{"role": "system", "content": "You are a helpful assistant"}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=False,
    )
    return response.choices[0].message.content