from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict

class LoginAPIView(APIView):
    permission_classes = []  # público
    authentication_classes = [] 

    def _primary_role_and_data(self, user):
        # Orden de prioridad: superuser/administrador, director, medico, operador, paciente, groups, default
            """
            Return a single primary role string and optional related model data.

            Priority:
             - is_superuser -> 'administrador'
             - is_staff -> 'staff'
             - related one-to-one profiles (checked in order)
             - groups (first group name lowercased)
             - fallback 'user'

            This simplified implementation only checks existence of the reverse
            attribute (e.g. `user.paciente`) and returns the matching role.
            """
            # 1) admin/staff flags
            if getattr(user, 'is_superuser', False):
                return 'administrador', None
            if getattr(user, 'is_staff', False):
                return 'staff', None

            # 2) related one-to-one profile reverse names (order is important)
            related_names = [
                ('director', 'director'),
                ('director_medico', 'director'),
                ('medico', 'medico'),
                ('operador_laboratorio', 'operador'),
                ('operador', 'operador'),
                ('paciente', 'paciente'),
            ]

            for attr_name, role_name in related_names:
                if hasattr(user, attr_name):
                    try:
                        inst = getattr(user, attr_name)
                    except Exception:
                        inst = None
                    # If reverse relation is a manager/queryset (FK many-to-one), skip
                    if inst is None:
                        continue
                    if hasattr(inst, 'all'):
                        # it's a queryset/manager, skip (we expect OneToOne)
                        continue
                    # found a related profile instance
                    try:
                        data = model_to_dict(inst, exclude=['user'])
                    except Exception:
                        data = None
                    return role_name, data

            # 3) groups fallback: take first group name
            groups = list(user.groups.values_list('name', flat=True))
            if groups:
                return groups[0].lower(), None

            # 4) default
            return 'user', None

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"success": False, "message": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)

        role, role_data = self._primary_role_and_data(user)
        print (self._primary_role_and_data(user))
            
        return Response({
            "success": True,
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
            "role": role
        }, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    def post(self, request):
        try:
            Token.objects.filter(user=request.user).delete()
        except Exception:
            pass
        logout(request)
        return Response({"success": True, "message": "Logout exitoso."})