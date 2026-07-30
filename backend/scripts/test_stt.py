import os

from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()

AUDIO_FILE = "scripts/test_audio.wav"


def main():
    deepgram = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY"))

    with open(AUDIO_FILE, "rb") as audio_file:
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_file.read(),
            model="nova-3",
            language="es",
            smart_format=True,
        )

    print(response.model_dump_json(indent=4))


if __name__ == "__main__":
    main()