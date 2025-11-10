from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from django.utils import timezone
import logging

from ..serializers import FertilizacionSerializer
from ..models import Fertilizacion

logger = logging.getLogger(__name__)


class CreateFertilizacionMixin(APIView):
    """Crea una fertilización; si es exitosa, intenta crear automáticamente un embrión.

    Respuesta estructura similar a CreateEmbrionMixin: devuelve errores de validación
    en 'errors' y mensajes claros.
    """
    def post(self, request):
        serializer = FertilizacionSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Errores de validación Fertilización: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos de la fertilización.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                fertilizacion = serializer.save()
                logger.info(f"Fertilización creada: {fertilizacion}")

                result = {
                    "success": True,
                    "message": "Fertilización registrada correctamente.",
                    "data": FertilizacionSerializer(fertilizacion).data
                }

                # No crear el embrión automáticamente por ahora; dejar la información en null
                result["embryo"] = None

                return Response(result, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Error de integridad al crear fertilización: {str(e)}")
            return Response({
                "success": False,
                "message": "Error de integridad al registrar la fertilización."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error inesperado al crear fertilización.")
            return Response({
                "success": False,
                "message": "Ocurrió un error al registrar la fertilización."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
