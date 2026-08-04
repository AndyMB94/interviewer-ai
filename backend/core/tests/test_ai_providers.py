import pytest

from core.ai_providers.base import LLMProvider, STTProvider, TTSProvider


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
