from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from ..serializers import SegundaConsultaSerializer
from ..models import SegundaConsulta
from .. import models as sc_models
from .. import serializers as sc_serializers
from PrimerConsulta.models import PrimeraConsulta
import logging

logger = logging.getLogger(__name__)


class CreateSegundaConsultaMixin:
    """
    Mixin para manejar la creación de SegundaConsulta.
    Sigue la misma estructura y formato de respuesta que CreatePrimeraConsultaMixin.
    """

    def create(self, request, *args, **kwargs):
        payload = request.data
        print("Payload recibido:", payload)
        
        # Helper to safely convert numeric-like strings to int or None
        def safe_int(v):
            try:
                if v is None or v == "":
                    return None
                return int(v)
            except (TypeError, ValueError):
                return None

        # Helper to safely convert to boolean
        def safe_bool(v):
            if v is None or v == "":
                return False
            if isinstance(v, bool):
                return v
            if isinstance(v, str):
                return v.lower() in ['true', '1', 'yes', 'on']
            return bool(v)

        # Normalizar datos principales de SegundaConsulta
        consulta_data = {}
        
        # Obtener primera_consulta (puede venir como ID o objeto)
        primera_consulta_id = safe_int(payload.get('primera_consulta_id')) or safe_int(payload.get('primera_consulta'))
        if primera_consulta_id:
            try:
                primera_consulta = PrimeraConsulta.objects.get(id=primera_consulta_id)
                consulta_data['primera_consulta'] = primera_consulta
            except PrimeraConsulta.DoesNotExist:
                return Response(
                    {"error": f"PrimeraConsulta con ID {primera_consulta_id} no encontrada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Extraer campos booleanos
        consulta_data['ovocito_viable'] = safe_bool(payload.get('ovocito_viable', False))
        consulta_data['semen_viable'] = safe_bool(payload.get('semen_viable', False))
        
        # Extraer campos de medicación
        consulta_data['tipo_medicacion'] = payload.get('tipo_medicacion')
        consulta_data['dosis_medicacion'] = payload.get('dosis_medicacion')
        consulta_data['duracion_medicacion'] = payload.get('duracion_medicacion')
        
        # Manejar consentimiento informado (archivo binario)
        if 'consentimiento_informado' in request.FILES:
            consulta_data['consentimiento_informado'] = request.FILES['consentimiento_informado'].read()
        elif payload.get('consentimiento_informado'):
            consulta_data['consentimiento_informado'] = payload.get('consentimiento_informado')

        try:
            with transaction.atomic():
                # Crear la segunda consulta
                serializer = SegundaConsultaSerializer(data=consulta_data)
                
                if serializer.is_valid():
                    segunda_consulta = serializer.save()
                    
                    logger.info(f"✅ SegundaConsulta creada exitosamente: ID {segunda_consulta.id}")
                    
                    # Preparar respuesta exitosa
                    response_data = {
                        "success": True,
                        "message": "Segunda consulta creada exitosamente",
                        "data": {
                            "segunda_consulta": SegundaConsultaSerializer(segunda_consulta).data
                        }
                    }
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"❌ Error en validación del serializer: {serializer.errors}")
                    return Response(
                        {
                            "success": False,
                            "message": "Error en los datos proporcionados",
                            "errors": serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
        except IntegrityError as e:
            logger.error(f"❌ Error de integridad en la base de datos: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Error de integridad en la base de datos",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"❌ Error inesperado al crear SegundaConsulta: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )