from enum import Enum


class InterviewState(str, Enum):
    ESPERANDO_RESPUESTA = "esperando_respuesta"
    TRANSCRIBIENDO = "transcribiendo"
    EVALUANDO = "evaluando"
    GENERANDO_AUDIO = "generando_audio"


class InvalidTransitionError(Exception):
    pass


class InterviewSession:
    TRANSITIONS = {
        InterviewState.ESPERANDO_RESPUESTA: {InterviewState.TRANSCRIBIENDO},
        InterviewState.TRANSCRIBIENDO: {InterviewState.EVALUANDO},
        InterviewState.EVALUANDO: {InterviewState.GENERANDO_AUDIO},
        InterviewState.GENERANDO_AUDIO: {InterviewState.ESPERANDO_RESPUESTA},
    }

    def __init__(self, state: InterviewState = InterviewState.ESPERANDO_RESPUESTA):
        self.state = state

    def transition_to(self, new_state: InterviewState) -> None:
        allowed = self.TRANSITIONS[self.state]
        if new_state not in allowed:
            raise InvalidTransitionError(
                f"No se puede pasar de '{self.state.value}' a '{new_state.value}'"
            )
        self.state = new_state
