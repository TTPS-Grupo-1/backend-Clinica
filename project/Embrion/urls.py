from rest_framework.routers import DefaultRouter
from .views.embrion_viewset import EmbrionViewSet

router = DefaultRouter()
router.register(r'embriones', EmbrionViewSet, basename='embrion')

urlpatterns = router.urls
