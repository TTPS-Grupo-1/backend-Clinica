from rest_framework.routers import DefaultRouter
from .views.fertilizacion_viewset import FertilizacionViewSet

router = DefaultRouter()
router.register(r'fertilizacion', FertilizacionViewSet, basename='fertilizacion')

urlpatterns = router.urls
