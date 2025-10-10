from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class CreateMedicoMixin:
    """
    Mixin para manejar la creación de médicos con mensajes personalizados.
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Validaciones del serializer
        if not serializer.is_valid():
            logger.warning(f"Errores de validación: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            medico = serializer.save()
            logger.info(f"Médico creado: {getattr(medico, 'dni', '')}")
            return Response({
                "success": True,
                "message": "Médico registrado correctamente.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            return Response({
                "success": False,
                "message": "El médico ya existe o hay un campo duplicado."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Error inesperado al crear médico.")
            return Response({
                "success": False,
                "message": "Ocurrió un error al registrar el médico."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
