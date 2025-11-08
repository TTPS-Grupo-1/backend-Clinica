from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Tratamiento
from .serializers import TratamientoSerializer, TratamientoCreateSerializer


class TratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de tratamientos.
    """
    queryset = Tratamiento.objects.all()
    permission_classes = []
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TratamientoCreateSerializer
        return TratamientoSerializer
    
    def get_queryset(self):
        """Filtrar tratamientos según el rol del usuario"""
        user = self.request.user
        queryset = Tratamiento.objects.all()

        if user.rol == 'PACIENTE':
            # Los pacientes solo ven sus propios tratamientos
            queryset = queryset.filter(paciente=user)
        elif user.rol == 'MEDICO':
            # Los médicos ven tratamientos que han asignado o de sus pacientes
            queryset = queryset.filter(Q(medico=user))
        
        return queryset.select_related('paciente', 'medico')
    
    @action(detail=False, methods=['get'])
    def mis_tratamientos(self, request):
        """Endpoint para obtener tratamientos del usuario actual (si es paciente)"""
        if request.user.rol != 'paciente':
            return Response(
                {'error': 'Este endpoint es solo para pacientes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        tratamientos = self.get_queryset().filter(paciente=request.user, activo=True)
        serializer = self.get_serializer(tratamientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtener solo tratamientos activos"""
        queryset = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path=r'por-paciente/(?P<paciente_id>\d+)')
    def tratamiento_por_paciente(self, request, paciente_id=None):
        """
        Devuelve el tratamiento activo del paciente especificado.
        Ejemplo: /api/tratamientos/por-paciente?paciente_id=1
        """
        print(f"🧩 Buscando tratamiento activo para paciente_id={paciente_id}")
        print("el rpj papap")
        tratamientos = (
            Tratamiento.objects
            .filter(paciente_id=paciente_id, activo=True)
            .order_by('-fecha_creacion')
        )

        if not tratamientos.exists():
            return Response(
                {"detail": f"No se encontró tratamiento activo para el paciente {paciente_id}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tratamiento = tratamientos.first()
        serializer = self.get_serializer(tratamiento)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=["patch"])
    def cancelar(self, request, pk=None):
        try:
            tratamiento = self.get_object()
            motivo = request.data.get("motivo_cancelacion", "").strip()

            if not motivo:
                return Response(
                    {"error": "Debe proporcionar un motivo de cancelación."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tratamiento.activo = False
            tratamiento.motivo_finalizacion = motivo
            tratamiento.save(update_fields=["activo", "motivo_finalizacion"])

            return Response(
                {"success": True, "message": "Tratamiento cancelado correctamente."},
                status=status.HTTP_200_OK,
            )

        except Tratamiento.DoesNotExist:
            return Response(
                {"error": "Tratamiento no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Error al cancelar el tratamiento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
