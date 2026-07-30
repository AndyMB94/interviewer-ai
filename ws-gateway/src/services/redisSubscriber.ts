import { createClient, RedisClientType } from "redis";

const REDIS_URL = "redis://localhost:6379";

let subscriberClient: RedisClientType | null = null;

async function getSubscriber() {
  if (!subscriberClient) {
    subscriberClient = createClient({ url: REDIS_URL });
    await subscriberClient.connect();
  }
  return subscriberClient;
}

export async function subscribeToTask(taskId: string, onMessage: (message: string) => void) {
  const subscriber = await getSubscriber();

  await subscriber.subscribe(`task:${taskId}`, (message) => {
    onMessage(message);
    subscriber.unsubscribe(`task:${taskId}`);
  });
}