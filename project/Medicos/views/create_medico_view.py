from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
import logging
from Medicos.models import Medico

logger = logging.getLogger(__name__)

class CreateMedicoMixin:
    """
    Mixin para manejar la creación de médicos con mensajes personalizados.
    """

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Validar que la contraseña esté presente
            if 'password' not in data or not data['password']:
                return Response(
                    {
                        "success": False,
                        "message": "La contraseña es requerida"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar longitud mínima de contraseña
            if len(data['password']) < 8:
                return Response(
                    {
                        "success": False,
                        "message": "La contraseña debe tener al menos 8 caracteres"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar si el email ya existe
            if 'email' in data and Medico.objects.filter(email=data['email']).exists():
                return Response(
                    {
                        "success": False,
                        "message": "El email ya está registrado"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar si el DNI ya existe
            if 'dni' in data and Medico.objects.filter(dni=data['dni']).exists():
                return Response(
                    {
                        "success": False,
                        "message": "El DNI ya está registrado"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Hashear la contraseña
            data['password'] = make_password(data['password'])
            
            serializer = self.get_serializer(data=data)
            
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
                error_msg = str(e).lower()
                logger.error(f"Error de integridad: {error_msg}")
                
                # Detectar específicamente qué campo está duplicado
                if 'email' in error_msg:
                    message = "El email ya está registrado"
                elif 'dni' in error_msg:
                    message = "El DNI ya está registrado"
                else:
                    message = "El médico ya existe o hay un campo duplicado"
                
                return Response({
                    "success": False,
                    "message": message
                }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                logger.exception("Error inesperado al crear médico.")
                return Response({
                    "success": False,
                    "message": "Ocurrió un error al registrar el médico."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.exception(f"Error general al crear médico: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": f"Error al crear médico: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
