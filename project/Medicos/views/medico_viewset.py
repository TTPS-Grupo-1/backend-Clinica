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
    # 🔹 Actualizar médico
    # --------------------------------------------------------
    def update(self, request, *args, **kwargs):
        logger.info(f"📥 Datos recibidos en update: {request.data}")
        logger.info(f"📋 FILES recibidos: {request.FILES}")
        
        partial = True  # 👈 FORZAR partial=True para que no pida campos requeridos
        instance = self.get_object()
        
        # Crear una copia mutable de los datos
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # El frontend siempre envía 'rol', pero lo ignoramos y mantenemos 'MEDICO'
        data['rol'] = 'MEDICO'
        
        # NO incluir dni ni password en la actualización
        data.pop('dni', None)
        data.pop('password', None)
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        
        if not serializer.is_valid():
            logger.error(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        
        logger.info(f"✅ Médico actualizado correctamente: {instance.email}")
        
        return Response({
            "success": True,
            "message": "Médico actualizado correctamente.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # --------------------------------------------------------
    # 🔹 Actualización parcial (PATCH)
    # --------------------------------------------------------
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

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
