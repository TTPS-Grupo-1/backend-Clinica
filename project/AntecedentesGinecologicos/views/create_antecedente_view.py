from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from ..serializers import AntecedentesGinecologicosSerializer
import logging

logger = logging.getLogger(__name__)


class CreateAntecedenteMixin:
    """
    Mixin para manejar la creación de antecedentes ginecológicos.
    Sigue el mismo formato de respuesta que `CreatePacienteMixin`.
    """

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            logger.warning(f"Errores de validación antecedentes: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Hay errores en los campos ingresados.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = serializer.save()
            logger.info(f"Antecedentes creados: {instance.id}")
            return Response(
                {
                    "success": True,
                    "message": "Antecedentes guardados correctamente.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Error de integridad en la base de datos.",
                    "errors": {"non_field_errors": ["Error de integridad en la base de datos."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception("Error inesperado al guardar antecedentes.")
            return Response(
                {
                    "success": False,
                    "message": "Ocurrió un problema técnico al guardar antecedentes. Por favor, intente nuevamente en unos momentos.",
                    "errors": {"server": [str(e)]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
