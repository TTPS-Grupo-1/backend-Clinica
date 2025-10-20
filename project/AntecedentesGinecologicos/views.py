"""
Archivo principal de vistas para la aplicación AntecedentesGinecologicos.

Este archivo importa y expone el ViewSet principal desde la estructura modular
en `AntecedentesGinecologicos/views/`, siguiendo el patrón de la app `Paciente`.

Estructura esperada:
- views/create_antecedente_view.py: Mixin de creación
- views/antecedente_viewset.py: ViewSet principal

Se exportan las clases principales para facilitar importaciones externas.
"""

# Importar el ViewSet principal desde la estructura modular
from .views.antecedente_viewset import AntecedentesGinecologicosViewSet

# Importar mixins individuales para uso específico si es necesario
from .views.create_antecedente_view import CreateAntecedenteMixin

__all__ = [
    'AntecedentesGinecologicosViewSet',
    'CreateAntecedenteMixin',
]

# Compatibilidad hacia atrás: mantener la clase disponible directamente
AntecedentesGinecologicosViewSet = AntecedentesGinecologicosViewSet
