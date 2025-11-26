from rest_framework.routers import DefaultRouter
from Turnos.views.turno_viewset import TurnoViewSet

router = DefaultRouter()
router.register(r'', TurnoViewSet, basename='turno')

urlpatterns = router.urls
