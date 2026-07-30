import os

import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.environ.get("REDIS_URL"))
r.publish("interview:test", "Hola desde el publisher")
print("Mensaje publicado")