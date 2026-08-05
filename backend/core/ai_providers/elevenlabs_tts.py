import os
import uuid

from django.conf import settings
from elevenlabs.client import ElevenLabs

from core.ai_providers.base import TTSProvider


class ElevenLabsTTS(TTSProvider):
    def synthesize(self, text: str) -> str:
        elevenlabs = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

        audio = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id="p5EUznrYaWnafKvUkNiR",
            model_id="eleven_v3",
            output_format="mp3_44100_128",
        )

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)

        with open(filepath, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return settings.MEDIA_URL + filename
