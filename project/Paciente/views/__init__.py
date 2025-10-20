"""
Paquete de vistas para la aplicación Paciente.

Este paquete contiene todas las vistas separadas por funcionalidad:
- create_paciente_view.py: Operaciones de creación
- update_paciente_view.py: Operaciones de actualización  
- delete_paciente_view.py: Operaciones de eliminación
- list_paciente_view.py: Operaciones de listado y lectura
- paciente_viewset.py: ViewSet principal que combina todas las operaciones
"""

# Importar todas las vistas para facilitar el acceso
from .paciente_viewset import PacienteViewSet

__all__ = [
    'PacienteViewSet'
]