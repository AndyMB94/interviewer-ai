import pytest

from core.ai_providers.base import LLMProvider, STTProvider, TTSProvider
from core.ai_providers.deepseek_llm import INTERVIEW_SYSTEM_PROMPT


def test_interview_system_prompt_has_anti_derail_guardrail():
    # Fase 10.17: el candidato no debería poder sacar a Gaby de su rol de entrevistadora
    # pidiéndole que cambie de tema, ignore sus instrucciones, o actúe como otra cosa.
    assert "REGLA ESTRICTA DE ROL" in INTERVIEW_SYSTEM_PROMPT
    assert "redirija con" in INTERVIEW_SYSTEM_PROMPT
    # A pedido explícito: repetir la misma pregunta pendiente, no pasar a una nueva -- si no,
    # el candidato podría usar el intento de sacarla de tema para evadir la pregunta original.
    assert "repita textualmente la misma pregunta" in INTERVIEW_SYSTEM_PROMPT


@pytest.mark.parametrize("provider_class", [LLMProvider, STTProvider, TTSProvider])
def test_provider_interfaces_cannot_be_instantiated_directly(provider_class):
    with pytest.raises(TypeError):
        provider_class()


def test_concrete_llm_provider_must_implement_ask():
    class FakeLLMProvider(LLMProvider):
        def ask(self, question: str, history: list[dict] | None = None) -> str:
            return "respuesta falsa"

    provider = FakeLLMProvider()
    assert provider.ask("¿hola?") == "respuesta falsa"
