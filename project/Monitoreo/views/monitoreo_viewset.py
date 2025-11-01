from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
import logging
from datetime import datetime
from ..models import Monitoreo
from ..serializers import MonitoreoSerializer
from Tratamiento.models import Tratamiento

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
        queryset = Monitoreo.objects.select_related('tratamiento', 'tratamiento__paciente', 'tratamiento__medico')
        
        # Filtrar por tratamiento
        tratamiento_id = self.request.query_params.get('tratamiento', None)
        if tratamiento_id:
            queryset = queryset.filter(tratamiento_id=tratamiento_id)
        
        # Filtrar por estado de atención
        atendido = self.request.query_params.get('atendido', None)
        if atendido is not None:
            queryset = queryset.filter(atendido=atendido.lower() == 'true')
        
        # Filtrar por paciente
        paciente_dni = self.request.query_params.get('paciente', None)
        if paciente_dni:
            queryset = queryset.filter(tratamiento__paciente__dni=paciente_dni)
        
        # ✅ NUEVO: Filtrar por rango de fechas de atención
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_atencion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_atencion__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_creacion')
    
    def create(self, request, *args, **kwargs):
        """
        Crea un monitoreo asociado a un tratamiento.
        El paciente y médico se obtienen automáticamente del tratamiento.
        """
        logger.info(f"📥 Datos recibidos: {request.data}")
        
        # Validar que venga el tratamiento
        tratamiento_id = request.data.get('tratamiento')
        if not tratamiento_id:
            logger.error("❌ No se proporcionó el ID del tratamiento")
            return Response({
                "success": False,
                "message": "El ID del tratamiento es requerido",
                "errors": {"tratamiento": ["Este campo es requerido"]}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que existe el tratamiento
        try:
            tratamiento = Tratamiento.objects.get(id=tratamiento_id)
            
            if not tratamiento.paciente:
                return Response({
                    "success": False,
                    "message": "El tratamiento no tiene un paciente asignado"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not tratamiento.medico:
                return Response({
                    "success": False,
                    "message": "El tratamiento no tiene un médico asignado"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Tratamiento.DoesNotExist:
            logger.error(f"❌ No existe tratamiento con ID {tratamiento_id}")
            return Response({
                "success": False,
                "message": f"No existe un tratamiento con ID {tratamiento_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        
        logger.info(f"✅ Monitoreo creado exitosamente")
        logger.info(f"   - Tratamiento ID: {tratamiento_id}")
        logger.info(f"   - Paciente: {tratamiento.paciente.first_name} {tratamiento.paciente.last_name}")
        logger.info(f"   - Médico: {tratamiento.medico.first_name} {tratamiento.medico.last_name}")
        if serializer.data.get('fecha_atencion'):
            logger.info(f"   - Fecha de atención programada: {serializer.data['fecha_atencion']}")
        
        return Response({
            "success": True,
            "message": "Monitoreo guardado correctamente.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un monitoreo
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
        """
        monitoreos = self.get_queryset().filter(
            tratamiento__paciente__dni=paciente_dni
        )
        
        serializer = self.get_serializer(monitoreos, many=True)
        return Response({
            "success": True,
            "count": monitoreos.count(),
            "data": serializer.data
        })
    
    # ✅ NUEVO: Endpoint para obtener monitoreos próximos a atender
    @action(detail=False, methods=['get'], url_path='proximos')
    def proximos(self, request):
        """
        Obtiene monitoreos con fecha de atención próxima (no atendidos)
        GET /api/monitoreo/monitoreos/proximos/
        """
        from django.utils import timezone
        
        monitoreos = self.get_queryset().filter(
            atendido=False,
            fecha_atencion__isnull=False,
            fecha_atencion__gte=timezone.now()
        ).order_by('fecha_atencion')
        
        serializer = self.get_serializer(monitoreos, many=True)
        
        return Response({
            "success": True,
            "count": monitoreos.count(),
            "data": serializer.data
        })
