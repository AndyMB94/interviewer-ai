from celery import shared_task

from apps.interviews.services.llm_service import ask_llm


@shared_task
def add(x, y):
    return x + y


@shared_task
def ask_llm_task(question):
    return ask_llm(question)