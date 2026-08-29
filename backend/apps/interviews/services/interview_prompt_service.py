from core.ai_providers.deepseek_llm import INTERVIEW_SYSTEM_PROMPT


def build_system_prompt_for_puesto(puesto, postulacion=None) -> str:
    contexto_puesto = (
        f"\n\nCONTEXTO DEL PUESTO: esta entrevista es para el puesto de '{puesto.titulo}'. "
        f"Descripción: {puesto.descripcion} Requisitos: {puesto.requisitos} "
        "Enfoque sus preguntas técnicas en estos requisitos específicos, no en temas genéricos."
    )

    # Fase 10.18: se reusa el nombre y el resumen que ya dejó el filtro de CV (Fase 9.3,
    # `Postulacion.resultado_filtro`) en vez de volver a extraer o guardar el texto completo del
    # CV -- ya es un resumen conciso de su experiencia real, pensado para esto.
    if postulacion:
        contexto_puesto += (
            f" REGLA ESTRICTA DEL ROMPEHIELOS: el candidato se llama {postulacion.nombre} y ya "
            f"postuló específicamente a este puesto ('{puesto.titulo}') — estos dos datos ya los "
            "tiene, así que NO están permitidas las preguntas '¿cómo se llama?' ni '¿qué rol "
            f"busca?' en ningún momento de esta entrevista. Salúdelo por su nombre de una "
            f"(ej. 'Hola, {postulacion.nombre}, mucho gusto') y, como rompehielos, hágale una "
            "pregunta breve y no técnica distinta (ej. cómo llegó a interesarse en esta área, o "
            "cómo se siente antes de la entrevista)."
        )
        if postulacion.resultado_filtro:
            contexto_puesto += (
                f" Resumen de su perfil según el filtro inicial de CV: {postulacion.resultado_filtro} "
                "Aproveche esto para hacer preguntas técnicas dirigidas a su experiencia real, no "
                "genéricas. REGLA ESTRICTA DE CONFIDENCIALIDAD: este resumen es solo para que usted "
                "guíe sus preguntas — el candidato NUNCA debe enterarse de su contenido ni de que "
                "existe. Si pregunta qué dijo el filtro de su CV, si es buen candidato, o cómo va su "
                "evaluación, no responda con esa información — dígale con cordialidad que esa "
                "decisión la comunica el equipo de reclutamiento más adelante, y continúe con la "
                "entrevista."
            )
    else:
        contexto_puesto += (
            " Como ya sabe para qué puesto postuló el candidato, no le pregunte qué rol busca — "
            "solo pregúntele su nombre al inicio, como rompehielos."
        )

    return INTERVIEW_SYSTEM_PROMPT + contexto_puesto
