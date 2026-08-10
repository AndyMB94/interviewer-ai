import json

from pypdf import PdfReader

from core.ai_providers.deepseek_llm import DeepSeekLLM

SCREENING_SYSTEM_PROMPT = (
    "Eres un evaluador de currículums para procesos de selección técnica. "
    "Te voy a dar el texto de un CV y la descripción de un puesto con sus requisitos. "
    "Tu trabajo es decidir si el candidato es un buen fit técnico para el puesto, basándote "
    "únicamente en experiencia, habilidades y formación relevantes al puesto. "
    "No consideres edad, género, nacionalidad ni ningún dato personal no relacionado a lo técnico. "
    "Respondé ÚNICAMENTE con un JSON válido, sin texto adicional ni markdown, con este formato exacto: "
    '{"decision": "aprobado" o "rechazado", "razon": "una o dos oraciones explicando por qué"}'
)


def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def screen_candidate(cv_text: str, puesto) -> dict:
    prompt = (
        f"Puesto: {puesto.titulo}\n\n"
        f"Descripción: {puesto.descripcion}\n\n"
        f"Requisitos: {puesto.requisitos}\n\n"
        "---\n\n"
        f"CV del candidato:\n{cv_text}"
    )

    raw_response = DeepSeekLLM().ask(prompt, system_prompt=SCREENING_SYSTEM_PROMPT)

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {"decision": None, "razon": "No se pudo interpretar la respuesta del filtro de IA."}
