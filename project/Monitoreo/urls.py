from rest_framework.routers import DefaultRouter
from .views import MonitoreoViewSet

router = DefaultRouter()
router.register(r'monitoreos', MonitoreoViewSet, basename='monitoreo')

urlpatterns = router.urls
