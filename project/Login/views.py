from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

User = get_user_model()


class LoginAPIView(APIView):
    """
    Endpoint de autenticación para el sistema de clínica.
    Usa email y password (no username).
    Devuelve el token, los datos básicos del usuario y su rol.
    """
    permission_classes = []  # público
    authentication_classes = [] 

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validación de campos obligatorios
        if not email or not password:
            return Response(
                {"success": False, "message": "Debe ingresar email y contraseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Autenticación con email (Django usa USERNAME_FIELD del modelo)
        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"success": False, "message": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Evitar login de usuarios marcados como eliminados
        if getattr(user, 'eliminado', False):
            return Response(
                {"success": False, "message": "Este usuario está deshabilitado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Crear o recuperar token
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)

        # Armar respuesta
        return Response({
            "success": True,
            "message": "Inicio de sesión exitoso.",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "dni": user.dni,
                "telefono": user.telefono,
                "rol": user.rol,
                "gender": user.sexo,
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    Cierra la sesión y elimina el token del usuario autenticado.
    """

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(
            {"success": True, "message": "Sesión cerrada correctamente."},
            status=status.HTTP_200_OK,
        )
