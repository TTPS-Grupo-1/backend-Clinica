"""
Paquete de vistas para la aplicación Medicos.
Se exponen los ViewSets y mixins necesarios para la API.
"""
from .medico_viewset import MedicoViewSet
from CustomUser.views.create_user_mixin import CreateUserMixin

__all__ = [
    'MedicoViewSet',
    'CreateUserMixin'
]

# Compatibilidad hacia atrás
MedicoViewSet = MedicoViewSet
