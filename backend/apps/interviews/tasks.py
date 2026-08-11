import base64

import redis
from celery import shared_task
from django.conf import settings

from apps.interviews.models import Answer, Question
from apps.interviews.services.interview_prompt_service import build_system_prompt_for_puesto
from core.ai_providers.deepgram_stt import DeepgramSTT
from core.ai_providers.deepseek_llm import DeepSeekLLM
from core.ai_providers.elevenlabs_tts import ElevenLabsTTS

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


def publish_result(task_id, result):
    redis_client.publish(f"task:{task_id}", result)


@shared_task
def add(x, y):
    return x + y


@shared_task(bind=True)
def ask_llm_task(self, question_id):
    question = Question.objects.select_related("interview__postulacion__puesto").get(pk=question_id)

    history = []
    previous_questions = (
        Question.objects.filter(interview=question.interview)
        .exclude(pk=question.pk)
        .order_by("created_at")
    )
    for previous_question in previous_questions:
        history.append({"role": "user", "content": previous_question.text})
        if hasattr(previous_question, "answer"):
            history.append({"role": "assistant", "content": previous_question.answer.text})

    postulacion = question.interview.postulacion
    system_prompt = build_system_prompt_for_puesto(postulacion.puesto) if postulacion else None

    answer_text = DeepSeekLLM().ask(question.text, history=history, system_prompt=system_prompt)
    Answer.objects.create(question=question, text=answer_text)

    publish_result(self.request.id, answer_text)
    return answer_text


@shared_task(bind=True)
def transcribe_audio_task(self, audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    transcript = DeepgramSTT().transcribe(audio_bytes)
    publish_result(self.request.id, transcript)
    return transcript


@shared_task(bind=True)
def synthesize_speech_task(self, text):
    audio_url = ElevenLabsTTS().synthesize(text)
    publish_result(self.request.id, audio_url)
    return audio_url