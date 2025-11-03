from rest_framework.routers import DefaultRouter
from .views.segunda_viewset import SegundaConsultaViewSet

router = DefaultRouter()
router.register(r'', SegundaConsultaViewSet, basename='segunda_consultas')

urlpatterns = router.urls