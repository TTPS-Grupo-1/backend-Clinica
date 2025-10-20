from django.shortcuts import render
from .views.embrion_viewset import EmbrionViewSet # para uso específico si es necesario
from .views.create_embrion_view import CreatePuncionMixin

# Exponer las clases principales para importación externa
__all__ = [
    'EmbrionViewSet',          # ViewSet principal completo
    'CreateEmbrionMixin',      # Mixin de creación
]

EmbrionViewSet = EmbrionViewSet