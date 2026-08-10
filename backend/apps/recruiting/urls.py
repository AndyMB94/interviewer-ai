from rest_framework.routers import DefaultRouter

from apps.recruiting.views import PuestoViewSet

router = DefaultRouter()
router.register("puestos", PuestoViewSet, basename="puesto")

urlpatterns = router.urls
