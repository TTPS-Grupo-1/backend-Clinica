from rest_framework.routers import DefaultRouter
from .views.puncion_viewset import PuncionViewSet

router = DefaultRouter()
router.register(r'punciones', PuncionViewSet, basename='puncion')

urlpatterns = router.urls
