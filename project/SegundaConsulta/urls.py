from rest_framework.routers import DefaultRouter
from .views.segunda_viewset import SegundaConsultaViewSet

router = DefaultRouter()
router.register(r'segundas-consultas', SegundaConsultaViewSet, basename='segunda-consulta')

urlpatterns = router.urls