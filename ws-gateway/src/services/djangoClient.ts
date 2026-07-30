const DJANGO_URL = "http://localhost:8000";

export async function askQuestion(question: string): Promise<string> {
  const askResponse = await fetch(`${DJANGO_URL}/api/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const { task_id } = await askResponse.json();

  return pollResult(task_id);
}

async function pollResult(taskId: string): Promise<string> {
  while (true) {
    const response = await fetch(`${DJANGO_URL}/api/ask/${taskId}/`);
    const data = await response.json();

    if (data.status === "done") {
      return data.answer;
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}