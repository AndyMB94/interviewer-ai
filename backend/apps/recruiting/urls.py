from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.recruiting.views import CategoriaViewSet, PostulacionViewSet, PuestoViewSet, mi_postulacion

router = DefaultRouter()
router.register("puestos", PuestoViewSet, basename="puesto")
router.register("postulaciones", PostulacionViewSet, basename="postulacion")
router.register("categorias", CategoriaViewSet, basename="categoria")

# antes del router: "mia" no debe caer en el patrón <pk> de postulaciones/<pk>/ del router
urlpatterns = [
    path("postulaciones/mia/", mi_postulacion, name="mi_postulacion"),
] + router.urls
