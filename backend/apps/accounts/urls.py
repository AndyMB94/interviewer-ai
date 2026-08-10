from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.CookieTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.logout, name="logout"),
    path("ubigeo/departamentos/", views.ubigeo_departamentos, name="ubigeo_departamentos"),
    path("ubigeo/provincias/", views.ubigeo_provincias, name="ubigeo_provincias"),
    path("ubigeo/distritos/", views.ubigeo_distritos, name="ubigeo_distritos"),
]
