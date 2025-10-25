from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import logging
from CustomUser.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class MedicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para la gestión de médicos.
    Usa el modelo CustomUser (rol='MEDICO').
    """
    serializer_class = CustomUserSerializer
    lookup_field = 'dni'

    # --------------------------------------------------------
    # 🔹 Obtener médicos (solo rol=MEDICO y no eliminados)
    # --------------------------------------------------------
    def get_queryset(self):
        queryset = User.objects.filter(rol='MEDICO')
        if self.request.query_params.get('incluir_eliminados') != 'true':
            queryset = queryset.filter(eliminado=False)
        return queryset.order_by('last_name', 'first_name')

    # --------------------------------------------------------
    # 🔹 Crear médico (forzando el rol)
    # --------------------------------------------------------
    def perform_create(self, serializer):
        password = self.request.data.get('password')
        if not password:
            raise ValueError("El campo 'password' es obligatorio para crear un médico.")
        serializer.save(password=password, rol='MEDICO')

    # --------------------------------------------------------
    # 🔹 Eliminado lógico
    # --------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.eliminado = True
        instance.save()
        logger.info(f"🗑️ Médico eliminado: {instance.email} ({instance.dni})")
        return Response(
            {"success": True, "message": "Médico eliminado correctamente."},
            status=status.HTTP_200_OK,
        )
