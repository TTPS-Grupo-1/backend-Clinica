from rest_framework import viewsets
from ..models import PrimeraConsulta
from ..serializers import PrimeraConsultaSerializer
from .create_primera_view import CreatePrimeraConsultaMixin
import logging

logger = logging.getLogger(__name__)


class PrimeraConsultaViewSet(
    CreatePrimeraConsultaMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de primeras consultas.
    Sigue el patrón del `PacienteViewSet` (mixins por operación + ModelViewSet).

    Endpoints disponibles:
    - GET/POST   /api/primeras-consultas/
    - GET/PUT/PATCH/DELETE /api/primeras-consultas/{id}/
    """
    queryset = PrimeraConsulta.objects.all()
    serializer_class = PrimeraConsultaSerializer
