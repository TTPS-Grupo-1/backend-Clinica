from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Monitoreo.views.monitoreo_viewset import MonitoreoViewSet

router = DefaultRouter()
router.register(r'monitoreos', MonitoreoViewSet, basename='monitoreo')

urlpatterns = [
    path('', include(router.urls)),
]
