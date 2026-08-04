from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def ask(self, question: str, history: list[dict] | None = None) -> str: ...


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str: ...


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> str: ...
