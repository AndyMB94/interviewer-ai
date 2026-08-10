from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.CookieTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.logout, name="logout"),
]
