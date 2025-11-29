from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests

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
    """

    queryset = PrimeraConsulta.objects.all()
    serializer_class = PrimeraConsultaSerializer


    @action(detail=False, methods=['get'], url_path='fenotipos')
    def obtener_fenotipos(self, request):
        """
        Proxy para obtener los fenotipos desde la Edge Function de Supabase
        evitando el problema de CORS en el frontend.
        """
        url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/fenotipos"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            logger.error(f"Error obteniendo fenotipos desde Supabase: {e}")
            return Response(
                {"error": "No se pudieron obtener los fenotipos."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
