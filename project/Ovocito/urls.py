from rest_framework.routers import DefaultRouter
from .views import OvocitoViewSet

router = DefaultRouter()
router.register(r'ovocitos', OvocitoViewSet, basename='ovocito')

urlpatterns = router.urls