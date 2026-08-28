import { subscribeToTask } from "./redisSubscriber.js";

const DJANGO_URL = process.env.DJANGO_URL || "http://localhost:8000";
// Autentica al gateway ante Django (Infra Fase 7) -- estas llamadas son de servidor a servidor,
// nunca traen el JWT de un usuario, así que Django necesita otra forma de confirmar que vienen
// del gateway y no de cualquiera pegándole directo a la API.
const GATEWAY_SHARED_SECRET = process.env.GATEWAY_SHARED_SECRET || "";

export async function askQuestion(
  question: string,
  interviewId?: number,
  token?: string,
  postulacionId?: number,
): Promise<{ answer: string; interviewId: number; createdAt?: string; timedOut?: boolean }> {
  const body: Record<string, unknown> = { question };
  if (interviewId) {
    body.interview_id = interviewId;
  } else if (postulacionId) {
    // postulacion_id solo importa al crear la Interview (primer mensaje) -- ver Backend 9.7.3
    body.postulacion_id = postulacionId;
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Gateway-Secret": GATEWAY_SHARED_SECRET,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const askResponse = await fetch(`${DJANGO_URL}/api/ask/`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const data = await askResponse.json();

  // Fase 10.9: el backend corta la entrevista él mismo a los 30 minutos -- no hay task_id que
  // esperar en ese caso, la respuesta ya viene con el mensaje de "se acabó el tiempo".
  if (data.timed_out) {
    return { answer: data.message, interviewId: data.interview_id, timedOut: true };
  }

  const { task_id, interview_id, created_at } = data;

  return new Promise((resolve) => {
    subscribeToTask(task_id, (answer) => {
      resolve({ answer, interviewId: interview_id, createdAt: created_at });
    });
  });
}

export async function transcribeAudio(audioBuffer: ArrayBuffer): Promise<string> {
  const formData = new FormData();
  formData.append("audio", new Blob([audioBuffer]), "audio.webm");

  const transcribeResponse = await fetch(`${DJANGO_URL}/api/transcribe/`, {
    method: "POST",
    headers: { "X-Gateway-Secret": GATEWAY_SHARED_SECRET },
    body: formData,
  });
  const { task_id } = await transcribeResponse.json();

  return new Promise((resolve) => {
    subscribeToTask(task_id, (transcript) => {
      resolve(transcript);
    });
  });
}

export async function finishInterview(interviewId: number): Promise<void> {
  await fetch(`${DJANGO_URL}/api/interviews/${interviewId}/finish/`, {
    method: "POST",
    headers: { "X-Gateway-Secret": GATEWAY_SHARED_SECRET },
  });
}

export async function synthesizeSpeech(text: string): Promise<string> {
  const speakResponse = await fetch(`${DJANGO_URL}/api/speak/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Gateway-Secret": GATEWAY_SHARED_SECRET },
    body: JSON.stringify({ text }),
  });
  const { task_id } = await speakResponse.json();

  return new Promise((resolve) => {
    subscribeToTask(task_id, (audioUrl) => {
      resolve(audioUrl);
    });
  });
}