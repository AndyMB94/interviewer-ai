import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

elevenlabs = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

audio = elevenlabs.text_to_speech.convert(
    text="Hola, bienvenido a la entrevista técnica.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v3",
    output_format="mp3_44100_128",
)

with open("scripts/test_tts_output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Audio guardado en scripts/test_tts_output.mp3")