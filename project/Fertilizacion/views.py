from django.shortcuts import render
from .views.fertilizacion_viewset import FertilizacionViewSet # para uso específico si es necesario
from .views.create_fertilizacion_view import CreateFertilizacionMixin

# Exponer las clases principales para importación externa
__all__ = [
    'FertilizacionViewSet',          # ViewSet principal completo
    'CreateFertilizacionMixin',      # Mixin de creación
]
FertilizacionViewSet = FertilizacionViewSet