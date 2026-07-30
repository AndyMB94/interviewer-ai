import os

from deepgram import DeepgramClient


def transcribe_audio(audio_bytes: bytes) -> str:
    deepgram = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY"))
    response = deepgram.listen.v1.media.transcribe_file(
        request=audio_bytes,
        model="nova-3",
        language="es",
        smart_format=True,
    )
    return response.results.channels[0].alternatives[0].transcript