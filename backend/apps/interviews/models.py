from django.conf import settings
from django.db import models

# Create your models here.

class Interview(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "En progreso"
        FINISHED = "finished", "Finalizada"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    def __str__(self):
        return f"Interview #{self.pk} ({self.status})"


class Question(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question #{self.pk} (interview {self.interview_id})"


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="answer")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer #{self.pk} (question {self.question_id})"