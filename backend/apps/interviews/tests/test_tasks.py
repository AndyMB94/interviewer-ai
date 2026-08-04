from unittest.mock import patch

import pytest

from apps.interviews.models import Answer, Interview, Question
from apps.interviews.tasks import ask_llm_task


@pytest.mark.django_db
@patch("apps.interviews.tasks.DeepSeekLLM")
@patch("apps.interviews.tasks.publish_result")
def test_ask_llm_task_saves_answer(mock_publish, mock_llm_class):
    mock_llm_class.return_value.ask.return_value = "respuesta simulada"

    interview = Interview.objects.create()
    question = Question.objects.create(interview=interview, text="Hola")

    result = ask_llm_task(question.id)

    assert result == "respuesta simulada"
    answer = Answer.objects.get(question=question)
    assert answer.text == "respuesta simulada"


@pytest.mark.django_db
@patch("apps.interviews.tasks.DeepSeekLLM")
@patch("apps.interviews.tasks.publish_result")
def test_ask_llm_task_includes_conversation_history(mock_publish, mock_llm_class):
    mock_llm_class.return_value.ask.return_value = "segunda respuesta"

    interview = Interview.objects.create()
    first_question = Question.objects.create(interview=interview, text="Me llamo Andy")
    Answer.objects.create(question=first_question, text="Encantado, Andy")

    second_question = Question.objects.create(interview=interview, text="¿Cómo me llamo?")

    ask_llm_task(second_question.id)

    _, kwargs = mock_llm_class.return_value.ask.call_args
    assert kwargs["history"] == [
        {"role": "user", "content": "Me llamo Andy"},
        {"role": "assistant", "content": "Encantado, Andy"},
    ]