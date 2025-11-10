from rest_framework import viewsets
from ..models import SegundaConsulta
from ..serializers import SegundaConsultaSerializer
from .create_segunda import CreateSegundaConsultaMixin
import logging

logger = logging.getLogger(__name__)


class SegundaConsultaViewSet(
    CreateSegundaConsultaMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de segundas consultas.
    Sigue el patrón del `PrimeraConsultaViewSet` (mixins por operación + ModelViewSet).

    Endpoints disponibles:
    - GET/POST   /api/segundas-consultas/
    - GET/PUT/PATCH/DELETE /api/segundas-consultas/{id}/
    """
    queryset = SegundaConsulta.objects.all()
    serializer_class = SegundaConsultaSerializer

    def get_queryset(self):
        """
        Opcionalmente filtra las consultas por primera_consulta si se proporciona como parámetro.
        """
        queryset = SegundaConsulta.objects.all()
        primera_consulta_id = self.request.query_params.get('primera_consulta', None)
        
        if primera_consulta_id is not None:
            queryset = queryset.filter(primera_consulta_id=primera_consulta_id)
            
        return queryset.order_by('-fecha')
