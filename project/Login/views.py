from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LoginAPIView(APIView):
    permission_classes = []  # público

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"success": False, "message": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({"success": True, "token": token.key, "user": {"id": user.id, "username": user.username}})

class LogoutAPIView(APIView):
    def post(self, request):
        try:
            Token.objects.filter(user=request.user).delete()
        except Exception:
            pass
        logout(request)
        return Response({"success": True, "message": "Logout exitoso."}) 
# Create your views here.
