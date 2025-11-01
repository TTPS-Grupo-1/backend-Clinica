from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
import logging
from ..models import Monitoreo
from ..serializers import MonitoreoSerializer

logger = logging.getLogger(__name__)

class MonitoreoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Monitoreos
    """
    queryset = Monitoreo.objects.all()
    serializer_class = MonitoreoSerializer
    
    def get_queryset(self):
        """
        Filtra monitoreos opcionalmente por tratamiento, paciente o estado
        """
        queryset = Monitoreo.objects.all()
        
        # Filtrar por tratamiento si viene en query params
        tratamiento_id = self.request.query_params.get('tratamiento', None)
        if tratamiento_id:
            queryset = queryset.filter(tratamiento_id=tratamiento_id)
        
        # Filtrar por estado de atención
        atendido = self.request.query_params.get('atendido', None)
        if atendido is not None:
            queryset = queryset.filter(atendido=atendido.lower() == 'true')
        
        # Filtrar por paciente (cuando exista Tratamiento)
        # paciente_dni = self.request.query_params.get('paciente', None)
        # if paciente_dni:
        #     queryset = queryset.filter(tratamiento__paciente__dni=paciente_dni)
        
        return queryset.order_by('-fecha_creacion')
    
    def create(self, request, *args, **kwargs):
        """
        Personaliza la creación de monitoreos
        """
        logger.info(f"📥 Datos recibidos: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        logger.info(f"✅ Monitoreo creado: {serializer.data}")
        
        return Response({
            "success": True,
            "message": "Monitoreo guardado correctamente.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Personaliza la actualización de monitoreos
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        logger.info(f"📥 Actualizando monitoreo {instance.id}: {request.data}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            logger.error(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        logger.info(f"✅ Monitoreo actualizado")
        
        return Response({
            "success": True,
            "message": "Monitoreo actualizado correctamente.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='marcar-atendido')
    def marcar_atendido(self, request, pk=None):
        """
        Marca un monitoreo como atendido
        PATCH /api/monitoreo/monitoreos/{id}/marcar-atendido/
        """
        monitoreo = self.get_object()
        monitoreo.atendido = True
        monitoreo.save()
        
        serializer = self.get_serializer(monitoreo)
        
        logger.info(f"✅ Monitoreo {monitoreo.id} marcado como atendido")
        
        return Response({
            "success": True,
            "message": "Monitoreo marcado como atendido.",
            "data": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='no-atendidos')
    def no_atendidos(self, request):
        """
        Obtiene todos los monitoreos no atendidos
        GET /api/monitoreo/monitoreos/no-atendidos/
        """
        monitoreos = self.get_queryset().filter(atendido=False)
        serializer = self.get_serializer(monitoreos, many=True)
        
        return Response({
            "success": True,
            "count": monitoreos.count(),
            "data": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='por-paciente/(?P<paciente_dni>[^/.]+)')
    def por_paciente(self, request, paciente_dni=None):
        """
        Obtiene todos los monitoreos de un paciente específico
        GET /api/monitoreo/monitoreos/por-paciente/12345678/
        
        👉 Descomentar cuando exista Tratamiento
        """
        # monitoreos = self.get_queryset().filter(
        #     tratamiento__paciente__dni=paciente_dni
        # )
        
        # 👇 Por ahora devuelve lista vacía
        monitoreos = []
        
        serializer = self.get_serializer(monitoreos, many=True)
        return Response({
            "success": True,
            "count": len(monitoreos),
            "data": serializer.data
        })
