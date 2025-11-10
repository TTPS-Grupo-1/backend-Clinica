
# Importar todas las vistas para facilitar el acceso
from .create_puncion_view import CreatePuncionMixin
from .puncion_viewset import PuncionViewSet

__all__ = [
	'CreatePuncionMixin',
	'PuncionViewSet'
]
