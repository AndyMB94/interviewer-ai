import base64

import redis
from celery import shared_task
from django.conf import settings

from apps.interviews.models import Answer, Question
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
def ask_llm_task(self, question_id):
    question = Question.objects.select_related("interview").get(pk=question_id)

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

    answer_text = ask_llm(question.text, history=history)
    Answer.objects.create(question=question, text=answer_text)

    publish_result(self.request.id, answer_text)
    return answer_text


@shared_task
def transcribe_audio_task(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    return transcribe_audio(audio_bytes)


@shared_task
def synthesize_speech_task(text):
    return synthesize_speech(text)