from django.shortcuts import render
from .views.monitoreo_viewset import MonitoreoViewSet # para uso específico si es necesario
from .views.create_monitoreo_view import CreateMonitoreoMixin

# Exponer las clases principales para importación externa
__all__ = [
    'MonitoreoViewSet',          # ViewSet principal completo
    'CreateMonitoreoMixin',      # Mixin de creación
]

MonitoreoViewSet = MonitoreoViewSet
