from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("ask/", views.ask, name="ask"),
    path("ask/<str:task_id>/", views.ask_result, name="ask_result"),
    path("transcribe/", views.transcribe, name="transcribe"),
    path("transcribe/<str:task_id>/", views.transcribe_result, name="transcribe_result"),
    path("speak/", views.speak, name="speak"),
    path("speak/<str:task_id>/", views.speak_result, name="speak_result"),
    path("interviews/<int:interview_id>/", views.interview_detail, name="interview_detail"),
    path("interviews/<int:interview_id>/finish/", views.finish_interview, name="finish_interview"),
]