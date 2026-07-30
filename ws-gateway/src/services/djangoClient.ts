import { subscribeToTask } from "./redisSubscriber.js";

const DJANGO_URL = "http://localhost:8000";

export async function askQuestion(question: string): Promise<string> {
  const askResponse = await fetch(`${DJANGO_URL}/api/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const { task_id } = await askResponse.json();

  return new Promise((resolve) => {
    subscribeToTask(task_id, (answer) => {
      resolve(answer);
    });
  });
}

export async function transcribeAudio(audioBuffer: ArrayBuffer): Promise<string> {
  const formData = new FormData();
  formData.append("audio", new Blob([audioBuffer]), "audio.webm");

  const transcribeResponse = await fetch(`${DJANGO_URL}/api/transcribe/`, {
    method: "POST",
    body: formData,
  });
  const { task_id } = await transcribeResponse.json();

  return new Promise((resolve) => {
    subscribeToTask(task_id, (transcript) => {
      resolve(transcript);
    });
  });
}

export async function synthesizeSpeech(text: string): Promise<string> {
  const speakResponse = await fetch(`${DJANGO_URL}/api/speak/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const { task_id } = await speakResponse.json();

  return new Promise((resolve) => {
    subscribeToTask(task_id, (audioUrl) => {
      resolve(audioUrl);
    });
  });
}