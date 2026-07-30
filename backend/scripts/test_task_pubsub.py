import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import redis
from apps.interviews.tasks import ask_llm_task

r = redis.from_url(os.environ.get("REDIS_URL"))

task = ask_llm_task.delay("Hola")
print("Task ID:", task.id)

pubsub = r.pubsub()
pubsub.subscribe(f"task:{task.id}")

print(f"Escuchando el canal 'task:{task.id}'...")
for message in pubsub.listen():
    if message["type"] == "message":
        print("Resultado recibido:", message["data"].decode("utf-8"))
        break