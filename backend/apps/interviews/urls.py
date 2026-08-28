from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("ask/", views.ask, name="ask"),
    path("transcribe/", views.transcribe, name="transcribe"),
    path("speak/", views.speak, name="speak"),
    path("interviews/en-curso/", views.interview_en_curso, name="interview_en_curso"),
    path("interviews/<int:interview_id>/", views.interview_detail, name="interview_detail"),
    path("interviews/<int:interview_id>/finish/", views.finish_interview, name="finish_interview"),
    path(
        "interviews/<int:interview_id>/decision/",
        views.update_interview_decision,
        name="update_interview_decision",
    ),
]