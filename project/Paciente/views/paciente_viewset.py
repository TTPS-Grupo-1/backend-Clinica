from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import logging
from CustomUser.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para la gestión de pacientes.
    Usa el modelo CustomUser (rol='PACIENTE').
    
    Endpoints:
      - GET/POST /api/pacientes/
      - GET/PUT/PATCH/DELETE /api/pacientes/{id}/
    """
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

    # --------------------------------------------------------
    # 🔹 Queryset: solo pacientes activos o filtrados
    # --------------------------------------------------------
    def get_queryset(self):
        queryset = User.objects.filter(rol='PACIENTE')
        if self.request.query_params.get('incluir_eliminados') != 'true':
            queryset = queryset.filter(eliminado=False)
        return queryset.order_by('last_name', 'first_name')

    # --------------------------------------------------------
    # 🔹 Crear paciente (forzando el rol)
    # --------------------------------------------------------
    def perform_create(self, serializer):
        password = self.request.data.get('password')
        if not password:
            raise ValueError("El campo 'password' es obligatorio para crear un paciente.")
        serializer.save(password=password, rol='PACIENTE')

    # --------------------------------------------------------
    # 🔹 Eliminado lógico
    # --------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.eliminado = True
        instance.save()
        logger.info(f"🗑️ Paciente eliminado: {instance.email} ({instance.dni})")
        return Response(
            {"success": True, "message": "Paciente eliminado correctamente."},
            status=status.HTTP_200_OK,
        )
