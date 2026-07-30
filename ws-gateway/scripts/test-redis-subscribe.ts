import { createClient } from "redis";

const REDIS_URL = "redis://localhost:6379";

async function main() {
  const subscriber = createClient({ url: REDIS_URL });
  await subscriber.connect();

  await subscriber.subscribe("interview:test", (message) => {
    console.log("Mensaje recibido:", message);
  });

  console.log("Escuchando el canal 'interview:test'...");
}

main();