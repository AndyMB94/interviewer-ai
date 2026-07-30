import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.interviews.tasks import add

result = add.delay(2, 3)
print("Task ID:", result.id)
print("Resultado:", result.get(timeout=10))