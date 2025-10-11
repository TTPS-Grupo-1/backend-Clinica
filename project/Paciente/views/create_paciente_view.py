from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class CreatePacienteMixin:
    """
    Mixin para manejar la creación de pacientes junto con su usuario base.
    """

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            logger.warning(f"Errores de validación: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Hay errores en los campos ingresados.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Crear usuario base (el email ya fue validado en el serializer)
            user = User.objects.create_user(
                username=data["email"],
                password=data["contraseña"],
                email=data["email"],
                first_name=data["nombre"],
                last_name=data["apellido"],
            )

            # Guardar paciente vinculado
            paciente = serializer.save(user=user)
            logger.info(f"Paciente creado: {paciente.nombre} {paciente.apellido}")

            return Response(
                {
                    "success": True,
                    "message": "Paciente registrado correctamente.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            msg = str(e).lower()
            if "dni" in msg:
                return Response(
                    {
                        "success": False,
                        "message": "Ya existe un paciente registrado con este DNI.",
                        "errors": {
                            "dni": ["Ya existe un paciente registrado con este DNI."]
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": False,
                    "message": "Error de integridad en la base de datos.",
                    "errors": {
                        "non_field_errors": ["Error de integridad en la base de datos."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception("Error inesperado al crear paciente.")
            return Response(
                {
                    "success": False,
                    "message": "Ocurrió un error al registrar el paciente.",
                    "errors": {"server": ["Error interno del servidor"]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
