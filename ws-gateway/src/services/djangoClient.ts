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