import os

from deepgram import DeepgramClient

from core.ai_providers.base import STTProvider


class DeepgramSTT(STTProvider):
    def transcribe(self, audio_bytes: bytes) -> str:
        deepgram = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY"))
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3",
            language="es",
            smart_format=True,
        )
        return response.results.channels[0].alternatives[0].transcript
