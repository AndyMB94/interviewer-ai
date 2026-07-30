import pytest

from apps.interviews.models import Answer, Interview, Question


@pytest.mark.django_db
def test_interview_default_status():
    interview = Interview.objects.create()

    assert interview.status == Interview.Status.IN_PROGRESS
    assert interview.user is None


@pytest.mark.django_db
def test_question_belongs_to_interview():
    interview = Interview.objects.create()
    question = Question.objects.create(interview=interview, text="Hola, ¿cómo estás?")

    assert question.interview == interview
    assert interview.questions.count() == 1


@pytest.mark.django_db
def test_answer_belongs_to_question():
    interview = Interview.objects.create()
    question = Question.objects.create(interview=interview, text="Hola")
    answer = Answer.objects.create(question=question, text="¡Hola! ¿Cómo puedo ayudarte?")

    assert answer.question == question
    assert question.answer == answer