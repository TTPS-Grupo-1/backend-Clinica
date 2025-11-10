
# Importar todas las vistas para facilitar el acceso
from .create_embrion_view import CreateEmbrionMixin
from .embrion_viewset import EmbrionViewSet

__all__ = [
	'CreateEmbrionMixin',
	'EmbrionViewSet'
]

