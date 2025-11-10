from django.shortcuts import render
from .views.create_monitoreo_view import CreateMonitoreoMixin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from Monitoreo.models import Monitoreo
from Monitoreo.serializers import MonitoreoSerializer

# Exponer las clases principales para importación externa
__all__ = [
    'MonitoreoViewSet',          # ViewSet principal completo
    'CreateMonitoreoMixin',      # Mixin de creación
]

class MonitoreoViewSet(viewsets.ModelViewSet):
    queryset = Monitoreo.objects.all()
    serializer_class = MonitoreoSerializer

    @action(detail=True, methods=['patch'], url_path='guardar_atencion')
    def guardar_atencion(self, request, pk=None):
        """
        Marca un monitoreo como atendido y guarda la descripción.
        URL: /api/monitoreo/monitoreos/{id}/guardar_atencion/
        """
        monitoreo = self.get_object()
        
        # Validar que no esté ya atendido
        if monitoreo.atendido:
            return Response(
                {'error': 'Este monitoreo ya fue atendido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que venga descripción
        descripcion = request.data.get('descripcion', '').strip()
        if not descripcion:
            return Response(
                {'error': 'La descripción es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar el monitoreo
        monitoreo.descripcion = descripcion
        monitoreo.atendido = True
        monitoreo.fecha_realizado = timezone.now()  # Asegúrate de tener este campo
        monitoreo.save()
        
        serializer = self.get_serializer(monitoreo)
        return Response(
            {
                'message': 'Monitoreo atendido exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

MonitoreoViewSet = MonitoreoViewSet
