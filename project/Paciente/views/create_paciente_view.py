from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class CreatePacienteMixin:
    """
    Mixin para manejar la creación de pacientes con mensajes personalizados.
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
            paciente = serializer.save()
            logger.info(f"Paciente creado: {paciente.nombre} {paciente.apellido}")
            return Response({
                "success": True,
                "message": "Paciente registrado correctamente.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            # Analiza el mensaje de error para saber si es email o dni duplicado
            error_msg = str(e).lower()
            if 'email' in error_msg:
                return Response({
                    "success": False,
                    "message": "Ya existe un paciente registrado con este email.",
                    "errors": {"email": ["Ya existe un paciente registrado con este email."]}
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'dni' in error_msg:
                return Response({
                    "success": False,
                    "message": "Ya existe un paciente registrado con este DNI.",
                    "errors": {"dni": ["Ya existe un paciente registrado con este DNI."]}
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "success": False,
                    "message": "Error de integridad en la base de datos.",
                    "errors": {"non_field_errors": ["Error de integridad en la base de datos."]}
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Error inesperado al crear paciente.")
            return Response({
                "success": False,
                "message": "Ocurrió un error al registrar el paciente.",
                "errors": {"server": ["Error interno del servidor"]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)