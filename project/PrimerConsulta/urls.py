from rest_framework.routers import DefaultRouter
from .views import PrimeraConsultaViewSet

router = DefaultRouter()
router.register(r'primeras-consultas', PrimeraConsultaViewSet, basename='primer-consulta')

urlpatterns = router.urls
