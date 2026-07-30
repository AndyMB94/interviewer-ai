from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("ask/", views.ask, name="ask"),
    path("ask/<str:task_id>/", views.ask_result, name="ask_result"),
    path("transcribe/", views.transcribe, name="transcribe"),
    path("transcribe/<str:task_id>/", views.transcribe_result, name="transcribe_result"),
]