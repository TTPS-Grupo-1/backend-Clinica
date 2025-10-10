"""
Paquete de vistas para la aplicación Medicos.
Se exponen los ViewSets y mixins necesarios para la API.
"""
from .medico_viewset import MedicoViewSet
from .create_medico_view import CreateMedicoMixin

__all__ = [
    'MedicoViewSet',
    'CreateMedicoMixin'
]

# Compatibilidad hacia atrás
MedicoViewSet = MedicoViewSet
