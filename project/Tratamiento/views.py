from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Tratamiento
from .serializers import TratamientoSerializer, TratamientoCreateSerializer

# Imports para detalles completos
from Ovocito.models import Ovocito
from Ovocito.serializers import OvocitoSerializer
from Fertilizacion.models import Fertilizacion
from Fertilizacion.serializers import FertilizacionSerializer
from Embrion.models import Embrion
from Embrion.serializers import EmbrionSerializer


class TratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de tratamientos.
    """
    queryset = Tratamiento.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TratamientoCreateSerializer
        return TratamientoSerializer
    
    def get_queryset(self):
        """Filtrar tratamientos según el rol del usuario"""
        user = self.request.user
        # Posible filtro por query param 'medico' para permitir consultas dirigidas desde el frontend
        medico_param = self.request.query_params.get('medico')
        paciente_param = self.request.query_params.get('paciente')

        queryset = Tratamiento.objects.all()

        if medico_param:
            # Si se solicita, devolver tratamientos asociados al medico indicado (por id)
            try:
                medico_id = int(medico_param)
                # Filtrar por el campo 'medico' del tratamiento (relación directa)
                queryset = queryset.filter(medico_id=medico_id)
            except (ValueError, TypeError):
                # si el parámetro no es válido, devolvemos vacío
                return Tratamiento.objects.none()
        elif paciente_param:
            # Si se solicita, devolver tratamientos asociados al paciente indicado (por id)
            try:
                paciente_id = int(paciente_param)
                # Filtrar por el campo 'paciente' del tratamiento (relación directa)
                queryset = queryset.filter(paciente_id=paciente_id)
            except (ValueError, TypeError):
                # si el parámetro no es válido, devolvemos vacío
                return Tratamiento.objects.none()
        else:
            # Filtrado por rol por defecto (usar valores de rol en mayúsculas)
            if user.rol == 'PACIENTE':
                # Los pacientes solo ven sus propios tratamientos
                queryset = queryset.filter(paciente=user)
            elif user.rol == 'MEDICO':
                # Los médicos ven tratamientos que han asignado
                queryset = queryset.filter(medico=user)

        return queryset.select_related('paciente', 'medico')
    


    @action(detail=False, methods=['get'])
    def mis_tratamientos(self, request):
        """Endpoint para obtener tratamientos del usuario actual (si es paciente)"""
        if request.user.rol != 'PACIENTE':
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
    
    @action(detail=False, methods=['get'], url_path=r'por-medico/(?P<medico_id>\d+)')
    def tratamientos_por_medico(self, request, medico_id=None):
        """
        Devuelve los tratamientos asignados a un médico específico.
        Ejemplo: /api/tratamientos/por-medico/1/
        """
        print(f"🧩 Buscando tratamientos para medico_id={medico_id}")
        tratamientos = (
            Tratamiento.objects
            .filter(medico_id=medico_id)
            .order_by('-fecha_creacion')
        )

        serializer = self.get_serializer(tratamientos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='detalles-completos')
    def detalles_completos(self, request, pk=None):
        """
        Devuelve el tratamiento con todos los datos relacionados (ovocitos, embriones, fertilizaciones).
        Ejemplo: /api/tratamientos/1/detalles-completos/
        """
        try:
            # Obtener el tratamiento directamente sin filtros de get_queryset
            tratamiento = Tratamiento.objects.get(id=pk)
            
            # Serializar el tratamiento
            print(f"🔍 DEBUG: Serializando tratamiento...")
            tratamiento_data = self.get_serializer(tratamiento).data
            print(f"🔍 DEBUG: Tratamiento serializado correctamente")
            
            # Obtener ovocitos relacionados
            print(f"🔍 DEBUG: Obteniendo ovocitos...")
            ovocitos_data = []
            if tratamiento.puncion:
                print(f"🔍 DEBUG: Tratamiento tiene punción: {tratamiento.puncion.id}")
                # Si hay punción, obtener ovocitos de esa punción
                ovocitos = Ovocito.objects.filter(puncion=tratamiento.puncion)
                print(f"🔍 DEBUG: Encontrados {ovocitos.count()} ovocitos por punción")
                ovocitos_data = OvocitoSerializer(ovocitos, many=True).data
            else:
                print(f"🔍 DEBUG: Tratamiento sin punción, buscando por paciente: {tratamiento.paciente.id}")
                # Fallback: obtener ovocitos del paciente
                ovocitos = Ovocito.objects.filter(paciente=tratamiento.paciente)
                print(f"🔍 DEBUG: Encontrados {ovocitos.count()} ovocitos por paciente")
                ovocitos_data = OvocitoSerializer(ovocitos, many=True).data
            print(f"🔍 DEBUG: Ovocitos serializados: {len(ovocitos_data)} items")

            # Obtener fertilizaciones relacionadas a esos ovocitos
            print(f"🔍 DEBUG: Obteniendo fertilizaciones...")
            fertilizaciones_data = []
            if ovocitos_data:
                ovocitos_ids = [o.get('id_ovocito') for o in ovocitos_data if o.get('id_ovocito')]
                print(f"🔍 DEBUG: IDs de ovocitos para buscar fertilizaciones: {ovocitos_ids}")
                if ovocitos_ids:
                    fertilizaciones = Fertilizacion.objects.filter(ovocito__in=ovocitos_ids)
                    print(f"🔍 DEBUG: Encontradas {fertilizaciones.count()} fertilizaciones")
                    fertilizaciones_data = FertilizacionSerializer(fertilizaciones, many=True).data
                    print(f"🔍 DEBUG: Fertilizaciones serializadas: {len(fertilizaciones_data)} items")

            # Obtener embriones relacionados a esas fertilizaciones
            print(f"🔍 DEBUG: Obteniendo embriones...")
            embriones_data = []
            if fertilizaciones_data:
                fertilizaciones_ids = [f.get('id') for f in fertilizaciones_data if f.get('id')]
                print(f"🔍 DEBUG: IDs de fertilizaciones para buscar embriones: {fertilizaciones_ids}")
                if fertilizaciones_ids:
                    embriones = Embrion.objects.filter(fertilizacion__in=fertilizaciones_ids)
                    print(f"🔍 DEBUG: Encontrados {embriones.count()} embriones")
                    embriones_data = EmbrionSerializer(embriones, many=True).data
                    print(f"🔍 DEBUG: Embriones serializados: {len(embriones_data)} items")

            print(f"🔍 DEBUG: Preparando respuesta final...")
            response_data = {
                'tratamiento': tratamiento_data,
                'ovocitos': ovocitos_data,
                'fertilizaciones': fertilizaciones_data,
                'embriones': embriones_data
            }
            print(f"🔍 DEBUG: Respuesta preparada, enviando...")
            return Response(response_data, status=status.HTTP_200_OK)

        except Tratamiento.DoesNotExist:
            print(f"🚨 ERROR: Tratamiento con ID {pk} no encontrado")
            return Response(
                {"detail": f"Tratamiento con ID {pk} no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"🚨 ERROR en detalles_completos: {str(e)}")
            import traceback
            print(f"🚨 TRACEBACK: {traceback.format_exc()}")
            return Response(
                {"detail": f"Error obteniendo detalles completos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=['get'], url_path=r'por-paciente/(?P<paciente_id>\d+)')
    def tratamiento_por_paciente(self, request, paciente_id=None):
        """
        Devuelve el tratamiento activo del paciente especificado.
        Ejemplo: /api/tratamientos/por-paciente/123/
        """
        print(f"🧩 Buscando tratamiento activo para paciente_id={paciente_id}")
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

    @action(detail=False, methods=['get'], url_path=r'todos-por-paciente/(?P<paciente_id>\d+)')
    def todos_tratamientos_por_paciente(self, request, paciente_id=None):
        """
        Devuelve TODOS los tratamientos del paciente especificado (activos e inactivos).
        Ejemplo: /api/tratamientos/todos-por-paciente/123/
        """
        print(f"🧩 Buscando TODOS los tratamientos para paciente_id={paciente_id}")
        tratamientos = (
            Tratamiento.objects
            .filter(paciente_id=paciente_id)
            .order_by('-fecha_creacion')
        )

        serializer = self.get_serializer(tratamientos, many=True)
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
