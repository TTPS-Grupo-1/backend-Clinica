"""
Archivo principal de vistas para la aplicación PrimeraConsulta.

Este archivo importa y expone el ViewSet principal desde la estructura modular
en `PrimerConsulta/views/`, siguiendo el patrón de la app `Paciente`.

Estructura esperada:
- views/create_primera_view.py: Mixin de creación
- views/primera_viewset.py: ViewSet principal

Se exportan las clases principales para facilitar importaciones externas.
"""

# Importar el ViewSet principal desde la estructura modular
from .views.primera_viewset import PrimeraConsultaViewSet

# Importar mixins individuales para uso específico si es necesario
from .views.create_primera_view import CreatePrimeraConsultaMixin

__all__ = [
    'PrimeraConsultaViewSet',
    'CreatePrimeraConsultaMixin',
]

# Compatibilidad hacia atrás: mantener la clase disponible directamente
PrimeraConsultaViewSet = PrimeraConsultaViewSet
