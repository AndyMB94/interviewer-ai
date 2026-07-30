import os

import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.environ.get("REDIS_URL"))
pubsub = r.pubsub()
pubsub.subscribe("interview:test")

print("Escuchando el canal 'interview:test'...")
for message in pubsub.listen():
    if message["type"] == "message":
        print("Mensaje recibido:", message["data"].decode("utf-8"))