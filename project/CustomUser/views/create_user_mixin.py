from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CreateUserMixin:
    """
    Mixin genérico para crear usuarios (médicos, pacientes, admins)
    usando el modelo CustomUser.
    """

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)

            # Validar password
            password = data.get("password")
            if not password:
                return Response({"success": False, "message": "La contraseña es requerida"}, status=400)
            if len(password) < 8:
                return Response({"success": False, "message": "La contraseña debe tener al menos 8 caracteres"}, status=400)

            # Validar duplicados
            email = data.get("email")
            dni = data.get("dni")
            if email and User.objects.filter(email=email).exists():
                return Response({"success": False, "message": "El email ya está registrado"}, status=400)
            if dni and User.objects.filter(dni=dni).exists():
                return Response({"success": False, "message": "El DNI ya está registrado"}, status=400)

            # Validar serializer
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.warning(f"Errores de validación: {serializer.errors}")
                return Response({
                    "success": False,
                    "message": "Hay errores en los campos ingresados.",
                    "errors": serializer.errors
                }, status=400)

            validated_data = serializer.validated_data
            email = validated_data.get("email")


            firma_medico = validated_data.get("firma_medico")

            user = User.objects.create_user(
                email=validated_data.get("email"),
                password=password,
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
                dni=validated_data.get("dni"),
                telefono=validated_data.get("telefono", ""),
                rol=validated_data.get("rol", "MEDICO"),
                firma_medico=firma_medico,
            )

            output_serializer = self.get_serializer(user)
            logger.info(f"✅ Usuario creado: {user.first_name} {user.last_name} ({user.rol}) — ID {user.id}")

            return Response({
                "success": True,
                "message": "Usuario registrado correctamente.",
                "data": output_serializer.data
            }, status=201)

        except IntegrityError as e:
            msg = "El usuario ya existe o hay un campo duplicado"
            if "email" in str(e).lower():
                msg = "El email ya está registrado"
            elif "dni" in str(e).lower():
                msg = "El DNI ya está registrado"
            logger.error(f"Error de integridad: {e}")
            return Response({"success": False, "message": msg}, status=400)

        except Exception as e:
            logger.exception(f"Error inesperado al crear usuario: {e}")
            return Response({
                "success": False,
                "message": f"Error inesperado: {str(e)}"
            }, status=500)
