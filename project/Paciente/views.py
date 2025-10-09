"""
Archivo principal de vistas para la aplicación Paciente.

Este archivo importa y expone el ViewSet principal desde la estructura modular.
La lógica específica de cada operación está separada en archivos individuales
dentro del paquete views/ para mejor organización y mantenimiento.

Estructura:
- views/create_paciente_view.py: Operaciones de creación
- views/update_paciente_view.py: Operaciones de actualización
- views/delete_paciente_view.py: Operaciones de eliminación
- views/list_paciente_view.py: Operaciones de listado y búsqueda
- views/paciente_viewset.py: ViewSet principal que combina todo
"""

# Importar el ViewSet principal desde la estructura modular
from .views.paciente_viewset import PacienteViewSet

# Importar mixins individuales para uso específico si es necesario
from .views.create_paciente_view import CreatePacienteMixin

# Exponer las clases principales para importación externa
__all__ = [
    'PacienteViewSet',          # ViewSet principal completo
    'CreatePacienteMixin',      # Mixin de creación
]

# Compatibilidad hacia atrás - mantener la clase principal disponible directamente
# Esto permite que el código existente siga funcionando sin cambios
PacienteViewSet = PacienteViewSet