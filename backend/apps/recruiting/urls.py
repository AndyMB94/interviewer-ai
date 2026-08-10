from rest_framework.routers import DefaultRouter

from apps.recruiting.views import PostulacionViewSet, PuestoViewSet

router = DefaultRouter()
router.register("puestos", PuestoViewSet, basename="puesto")
router.register("postulaciones", PostulacionViewSet, basename="postulacion")

urlpatterns = router.urls
