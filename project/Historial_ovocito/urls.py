from rest_framework.routers import DefaultRouter
from .views import HistorialOvocitoViewSet

router = DefaultRouter()
router.register(r'', HistorialOvocitoViewSet, basename='historial_ovocito')

urlpatterns = router.urls
