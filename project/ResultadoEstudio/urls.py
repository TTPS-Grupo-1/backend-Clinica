from rest_framework.routers import DefaultRouter
from .views import ResultadoEstudioViewSet

router = DefaultRouter()
router.register(r'', ResultadoEstudioViewSet, basename='resultados-estudios')

urlpatterns = router.urls
