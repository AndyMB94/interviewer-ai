from core.ai_providers.deepseek_llm import INTERVIEW_SYSTEM_PROMPT


def build_system_prompt_for_puesto(puesto) -> str:
    contexto_puesto = (
        f"\n\nCONTEXTO DEL PUESTO: esta entrevista es para el puesto de '{puesto.titulo}'. "
        f"Descripción: {puesto.descripcion} Requisitos: {puesto.requisitos} "
        "Enfoque sus preguntas técnicas en estos requisitos específicos, no en temas genéricos. "
        "Como ya sabe para qué puesto postuló el candidato, no le pregunte qué rol busca — "
        "solo pregúntele su nombre al inicio."
    )
    return INTERVIEW_SYSTEM_PROMPT + contexto_puesto
