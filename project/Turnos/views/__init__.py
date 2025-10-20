
from .turno_viewset import TurnoViewSet


__all__ = [
    'TurnoViewSet',
    'CreateMedicoMixin'
]

# Compatibilidad hacia atrás
TurnoViewSet = TurnoViewSet
