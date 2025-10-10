"""
Paquete de vistas para la aplicación Ovocito.

Este paquete contiene todas las vistas separadas por funcionalidad:
- create_ovocito_view.py: Operaciones de creación
- list_ovocito_view.py: Operaciones de listado y lectura
- ovocito_viewset.py: ViewSet principal que combina todas las operaciones
"""

# Importar todas las vistas para facilitar el acceso
from .create_ovocito_view import CreateOvocitoMixin
from .ovocito_viewset import OvocitoViewSet

__all__ = [
    'CreateOvocitoMixin',
    'OvocitoViewSet'
]