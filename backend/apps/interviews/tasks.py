import base64

import redis
from celery import shared_task
from django.conf import settings

from apps.interviews.services.llm_service import ask_llm
from apps.interviews.services.stt_service import transcribe_audio
from apps.interviews.services.tts_service import synthesize_speech

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


def publish_result(task_id, result):
    redis_client.publish(f"task:{task_id}", result)


@shared_task
def add(x, y):
    return x + y


@shared_task(bind=True)
def ask_llm_task(self, question):
    answer = ask_llm(question)
    publish_result(self.request.id, answer)
    return answer


@shared_task(bind=True)
def transcribe_audio_task(self, audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    transcript = transcribe_audio(audio_bytes)
    publish_result(self.request.id, transcript)
    return transcript


@shared_task(bind=True)
def synthesize_speech_task(self, text):
    audio_url = synthesize_speech(text)
    publish_result(self.request.id, audio_url)
    return audio_url