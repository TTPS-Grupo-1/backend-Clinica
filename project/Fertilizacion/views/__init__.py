
# Importar todas las vistas para facilitar el acceso
from .create_fertilizacion_view import CreateFertilizacionMixin
from .fertilizacion_viewset import FertilizacionViewSet

__all__ = [
	'CreateFertilizacionMixin',
	'FertilizacionViewSet'
]
