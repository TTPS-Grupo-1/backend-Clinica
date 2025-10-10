from rest_framework.routers import DefaultRouter
from .views import MedicoViewSet

router = DefaultRouter()
router.register(r'medicos', MedicoViewSet, basename='medico')

urlpatterns = router.urls