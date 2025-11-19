"""
ViewSet principal que combina todas las operaciones de ovocitos.
Hereda de todos los mixins especializados para proporcionar funcionalidad completa.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Ovocito
from ..serializers import OvocitoSerializer
from .create_ovocito_view import CreateOvocitoMixin

import logging

logger = logging.getLogger(__name__)


class OvocitoViewSet(
    CreateOvocitoMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de ovocitos.
    Combina todas las operaciones de altas y funcionalidades avanzadas.

    Endpoints disponibles:
    - CRUD Básico:
      - GET/POST   /api/ovocitos/

    - Funcionalidades Avanzadas:
      - GET    /api/ovocitos/search/?q=Ovocito&type=identificador
      - GET    /api/ovocitos/statistics/
      - POST   /api/ovocitos/bulk_delete/
    """
    queryset = Ovocito.objects.all()
    serializer_class = OvocitoSerializer

    def get_queryset(self):
        """
        Filtrar ovocitos por paciente usando query parameters.
        Ejemplo: /api/ovocitos/?paciente=4
        """
        queryset = Ovocito.objects.all()
        paciente_id = self.request.query_params.get('paciente')
        
        if paciente_id:
            try:
                paciente_id = int(paciente_id)
                queryset = queryset.filter(paciente_id=paciente_id)
                logger.info(f"Filtrando ovocitos por paciente {paciente_id}")
            except ValueError:
                logger.warning(f"ID de paciente inválido en query params: {paciente_id}")
                return Ovocito.objects.none()
        
        return queryset.order_by('-id_ovocito')

    @action(detail=False, methods=['get'], url_path=r'por-paciente/(?P<paciente_id>\d+)')
    def ovocitos_por_paciente(self, request, paciente_id=None):
        """
        Devuelve todos los ovocitos de un paciente específico.
        Ejemplo: /api/ovocitos/por-paciente/4/
        """
        try:
            paciente_id = int(paciente_id)
            ovocitos = Ovocito.objects.filter(paciente_id=paciente_id).order_by('-id_ovocito')
            
            logger.info(f"Consultando ovocitos para paciente {paciente_id}: {ovocitos.count()} encontrados")
            
            serializer = self.get_serializer(ovocitos, many=True)
            return Response({
                'success': True,
                'count': ovocitos.count(),
                'ovocitos': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response({
                'success': False,
                'message': 'ID de paciente inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error obteniendo ovocitos del paciente {paciente_id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo ovocitos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(
    detail=False,
    methods=['get'],
    url_path=r'no-usados/(?P<paciente_id>\d+)'
)
    def ovocitos_no_usados_por_paciente(self, request, paciente_id=None):
        """
        Devuelve todos los ovocitos de un paciente donde usado=False.
        Ruta: /api/ovocitos/no-usados/<paciente_id>/
        """
        try:
            paciente_id = int(paciente_id)

            ovocitos = Ovocito.objects.filter(
                paciente_id=paciente_id,
                usado=False
            ).order_by('-id_ovocito')

            serializer = self.get_serializer(ovocitos, many=True)

            return Response({
                'success': True,
                'count': ovocitos.count(),
                'ovocitos': serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({
                'success': False,
                'message': "ID de paciente inválido"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error obteniendo ovocitos no usados del paciente {paciente_id}: {str(e)}")
            return Response({
                'success': False,
                'message': f"Error obteniendo ovocitos no usados: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
