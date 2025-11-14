from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistorialEmbrionViewSet

router = DefaultRouter()
router.register(r'historial-embriones', HistorialEmbrionViewSet, basename='historial-embrion')

urlpatterns = [
    path('', include(router.urls)),
]
