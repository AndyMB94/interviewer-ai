import base64

from celery import shared_task

from apps.interviews.services.llm_service import ask_llm
from apps.interviews.services.stt_service import transcribe_audio
from apps.interviews.services.tts_service import synthesize_speech


@shared_task
def add(x, y):
    return x + y


@shared_task
def ask_llm_task(question):
    return ask_llm(question)


@shared_task
def transcribe_audio_task(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    return transcribe_audio(audio_bytes)


@shared_task
def synthesize_speech_task(text):
    return synthesize_speech(text)