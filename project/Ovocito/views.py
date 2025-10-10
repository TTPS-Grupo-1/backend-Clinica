from django.shortcuts import render
# Importar el ViewSet principal desde la estructura modular
from .views.ovocito_viewset import OvocitoViewSet # para uso específico si es necesario
from .views.create_ovocito_view import CreateOvocitoMixin

# Exponer las clases principales para importación externa
__all__ = [
    'OvocitoViewSet',          # ViewSet principal completo
    'CreateOvocitoMixin',      # Mixin de creación
]

# Compatibilidad hacia atrás - mantener la clase principal disponible directamente
# Esto permite que el código existente siga funcionando sin cambios
OvocitoViewSet = OvocitoViewSet

