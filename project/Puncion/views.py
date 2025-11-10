from django.shortcuts import render
from .views.puncion_viewset import PuncionViewSet # para uso específico si es necesario
from .views.create_puncion_view import CreatePuncionMixin

# Exponer las clases principales para importación externa
__all__ = [
    'PuncionViewSet',          # ViewSet principal completo
    'CreatePuncionMixin',      # Mixin de creación
]

# Compatibilidad hacia atrás - mantener la clase principal disponible directamente
# Esto permite que el código existente siga funcionando sin cambios
PuncionViewSet = PuncionViewSet

