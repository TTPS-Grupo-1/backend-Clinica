"""
Paquete de vistas para la aplicación Monitoreo.
Se exponen los ViewSets y mixins necesarios para la API.
"""
from .monitoreo_viewset import MonitoreoViewSet
from .create_monitoreo_view import CreateMonitoreoMixin

__all__ = [
    'MonitoreoViewSet',
    'CreateMonitoreoMixin'
]

# Compatibilidad hacia atrás
MonitoreoViewSet = MonitoreoViewSet
