import pytest

from core.interview_session import InterviewSession, InterviewState, InvalidTransitionError


def test_valid_transitions_follow_the_full_cycle():
    session = InterviewSession()

    session.transition_to(InterviewState.TRANSCRIBIENDO)
    assert session.state == InterviewState.TRANSCRIBIENDO

    session.transition_to(InterviewState.EVALUANDO)
    assert session.state == InterviewState.EVALUANDO

    session.transition_to(InterviewState.GENERANDO_AUDIO)
    assert session.state == InterviewState.GENERANDO_AUDIO

    session.transition_to(InterviewState.ESPERANDO_RESPUESTA)
    assert session.state == InterviewState.ESPERANDO_RESPUESTA


def test_cannot_evaluar_sin_transcripcion_lista():
    session = InterviewSession()

    with pytest.raises(InvalidTransitionError):
        session.transition_to(InterviewState.EVALUANDO)


def test_invalid_transition_does_not_change_state():
    session = InterviewSession()

    with pytest.raises(InvalidTransitionError):
        session.transition_to(InterviewState.GENERANDO_AUDIO)

    assert session.state == InterviewState.ESPERANDO_RESPUESTA
