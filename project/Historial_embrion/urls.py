from rest_framework.routers import DefaultRouter
from .views import HistorialEmbrionViewSet

router = DefaultRouter()
router.register(r'historial_embriones', HistorialEmbrionViewSet, basename='historial_embrion')

urlpatterns = router.urls
