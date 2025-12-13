from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Tratamiento
from .serializers import TratamientoSerializer, TratamientoCreateSerializer
from rest_framework.decorators import action, permission_classes
# Imports para detalles completos
from Ovocito.models import Ovocito
from Ovocito.serializers import OvocitoSerializer
from Fertilizacion.models import Fertilizacion
from Fertilizacion.serializers import FertilizacionSerializer
from Embrion.models import Embrion
from Embrion.serializers import EmbrionSerializer
from AntecedentesGinecologicos.models import AntecedentesGinecologicos
from AntecedentesGinecologicos.serializers import AntecedentesGinecologicosSerializer
from AntecedentesPersonales.models import AntecedentesPersonales
from AntecedentesPersonales.serializers import AntecedentesPersonalesSerializer
from ResultadoEstudio.models import ResultadoEstudio
from ResultadoEstudio.serializers import ResultadoEstudioSerializer
from Orden.models import Orden
from Orden.serializers import OrdenDescargaSerializer
from PrimerConsulta.models import PrimeraConsulta
from PrimerConsulta.serializers import PrimeraConsultaSerializer
from SegundaConsulta.models import SegundaConsulta
from SegundaConsulta.serializers import SegundaConsultaSerializer
from CustomUser.models import CustomUser
from CustomUser.serializers import CustomUserSerializer
from Ovocito.models import Ovocito
from Embrion.models import Embrion
from Fertilizacion.models import Fertilizacion
from Historial_embrion.models import HistorialEmbrion
from Historial_ovocito.models import HistorialOvocito 
from django.utils import timezone


class TratamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de tratamientos.
    """
    queryset = Tratamiento.objects.all()
    # permission_classes = [IsAuthenticated]
    
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
            estado = tratamiento.estado_actual()
            # Serializar el tratamiento
            print(f"🔍 DEBUG: Tratamiento #{pk} encontrado, estado actual: {estado}")
            print(f"🔍 DEBUG: Serializando tratamiento...")
            tratamiento_data = self.get_serializer(tratamiento).data
            print(f"🔍 DEBUG: Tratamiento serializado correctamente")
            
            # ==========================================
            # 1. OVOCITOS - De TODAS las punciones del paciente en el rango del tratamiento
            # ==========================================
            print(f"\n{'='*60}")
            print(f"🔍 TRATAMIENTO #{pk} - Filtrando datos específicos")
            print(f"{'='*60}")
            # Definir rango de fechas del tratamiento
            fecha_inicio = tratamiento.fecha_inicio
            fecha_fin = getattr(tratamiento, 'fecha_modificacion', None) or getattr(tratamiento, 'fecha_fin', None) or timezone.now()
            # Normalizar a date para comparar con DateField como fecha_fertilizacion
            start_date = fecha_inicio.date() if hasattr(fecha_inicio, 'date') else fecha_inicio
            end_date = fecha_fin.date() if hasattr(fecha_fin, 'date') else fecha_fin
            
            # Obtener todas las punciones del paciente dentro del rango del tratamiento
            from Puncion.models import Puncion
            punciones_paciente = Puncion.objects.filter(paciente=tratamiento.paciente)
            print(f"📊 Total de punciones del paciente: {punciones_paciente.count()}")

            # Traer todas las punciones del paciente dentro del rango de fechas
            punciones = punciones_paciente
            if fecha_inicio:
                punciones = punciones.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                punciones = punciones.filter(fecha__lte=fecha_fin)
            print(f"📊 Punciones en rango ({fecha_inicio} → {fecha_fin}): {punciones.count()}")
            
            # Recolectar ovocitos del paciente, preferentemente vinculados a las punciones en rango
            ovocitos = []
            try:
                # Preferencia: ovocitos del paciente asociados a las punciones en rango
                ovocitos_qs = Ovocito.objects.filter(paciente=tratamiento.paciente)
                if punciones.exists():
                    ovocitos_qs = ovocitos_qs.filter(puncion__in=punciones)

                # Aplicar rango por fecha de creación si existe el campo
                if fecha_inicio:
                    if hasattr(Ovocito, 'created_at'):
                        ovocitos_qs = ovocitos_qs.filter(created_at__gte=fecha_inicio)
                if fecha_fin:
                    if hasattr(Ovocito, 'created_at'):
                        ovocitos_qs = ovocitos_qs.filter(created_at__lte=fecha_fin)

                ovocitos = list(ovocitos_qs)

                # Log por punción para visibilidad
                for puncion in punciones[:5]:
                    count_p = Ovocito.objects.filter(paciente=tratamiento.paciente, puncion=puncion).count()
                    print(f"   📌 Punción ID={puncion.id} ({puncion.fecha}): {count_p} ovocitos del paciente")
            except Exception as e:
                print(f"⚠️ Fallback ovocitos por paciente: {str(e)}")
                ovocitos = list(Ovocito.objects.filter(paciente=tratamiento.paciente))
            
            print(f"📊 Total ovocitos de todas las punciones: {len(ovocitos)}")
            if ovocitos:
                for ovo in ovocitos[:5]:  # Mostrar solo los primeros 5
                    print(f"   - Ovocito ID={ovo.id_ovocito}, identificador={ovo.identificador}, puncion_id={ovo.puncion_id}")
            
            ovocitos_data = OvocitoSerializer(ovocitos, many=True).data
            
            # ==========================================
            # 2. FERTILIZACIONES - De los ovocitos del paciente en el rango del tratamiento
            # ==========================================
            fertilizaciones_data = []
            fertilizaciones = []
            
            # Buscar fertilizaciones del paciente directamente
            # Preferir FK directo a paciente si existe; si no, usar relación por ovocito
            from django.db.models import Q
            fertilizaciones = Fertilizacion.objects.filter(
                Q(paciente_id=tratamiento.paciente_id) |
                Q(ovocito__isnull=False, ovocito__paciente_id=tratamiento.paciente_id)
            )
            # Asegurar consistencia: si existen con paciente_id distinto al del tratamiento, excluirlas
            fertilizaciones = fertilizaciones.exclude(~Q(paciente_id=tratamiento.paciente_id), paciente_id__isnull=False)
            print(f"\n📊 Fertilizaciones del paciente (antes de fechas): {fertilizaciones.count()}")

            # Aplicar filtro de fechas a fertilizaciones: por fecha_fertilizacion y/o created_at
            if start_date:
                # Filtrar por fecha_fertilizacion con límites inclusivos usando fechas
                fertilizaciones = fertilizaciones.filter(fecha_fertilizacion__gte=start_date)
            if end_date:
                fertilizaciones = fertilizaciones.filter(fecha_fertilizacion__lte=end_date)

            print(f"📊 Fertilizaciones encontradas (rango aplicado): {fertilizaciones.count()}")
            # Fallback: si no hay fertilizaciones en la ventana, intentar por paciente sin ventana
            if not fertilizaciones.exists():
                print("⚠️ Sin fertilizaciones en ventana. Probando fallback por paciente sin rango...")
                fertilizaciones = Fertilizacion.objects.filter(paciente_id=tratamiento.paciente_id)
                print(f"📊 Fallback fertilizaciones por paciente: {fertilizaciones.count()}")
            if fertilizaciones.exists():
                for fert in fertilizaciones[:5]:
                    print(f"   - Fertilización ID={getattr(fert, 'id_fertilizacion', fert.pk)}, ovocito_id={getattr(fert, 'ovocito_id', None)}")
            fertilizaciones_data = FertilizacionSerializer(fertilizaciones, many=True).data

            # ==========================================
            # 3. EMBRIONES - Solo de las fertilizaciones de este tratamiento
            # ==========================================
            # Obtener embriones asociados a las fertilizaciones filtradas o directamente por paciente/ventana
            embriones = []
            from Embrion.models import Embrion as EmbrionModel
            if fertilizaciones.exists():
                print(f"\n📊 Buscando embriones de las fertilizaciones...")
                embriones = list(EmbrionModel.objects.filter(fertilizacion__in=fertilizaciones))
            else:
                print(f"❌ Sin fertilizaciones filtradas - intentamos por paciente y ventana de fechas")
                embriones = list(
                    EmbrionModel.objects.filter(
                        fertilizacion__paciente_id=tratamiento.paciente_id,
                        fertilizacion__fecha_fertilizacion__gte=start_date,
                        fertilizacion__fecha_fertilizacion__lte=end_date,
                    )
                )
                if not embriones:
                    print("⚠️ Fallback embriones por paciente sin rango...")
                    embriones = list(
                        EmbrionModel.objects.filter(
                            fertilizacion__paciente_id=tratamiento.paciente_id
                        )
                    )
            for emb in embriones[:5]:
                print(
                    f"   - Embrión ID={emb.id}, identificador={getattr(emb, 'identificador', '-')}, fertilizacion_id={getattr(emb, 'fertilizacion_id', '-')}" 
                )
            
            print(f"\n✅ RESUMEN:")
            print(f"   Ovocitos: {len(ovocitos_data)}")
            print(f"   Fertilizaciones: {len(fertilizaciones_data)}")
            print(f"   Embriones: {len(embriones)}")
            print(f"{'='*60}\n")
            
            embriones_data = EmbrionSerializer(embriones, many=True).data

            # Obtener datos relacionados con primera consulta
            print(f"🔍 DEBUG: Obteniendo datos de primera consulta...")
            primera_consulta_data = None
            antecedentes_ginecologicos_data = []
            antecedentes_personales_data = []
            resultados_estudios_data = []
            ordenes_data = []
            
            if tratamiento.primera_consulta:
                primera_consulta = tratamiento.primera_consulta
                print(f"🔍 DEBUG: Tratamiento tiene primera consulta: {primera_consulta.id}")
                
                # 🔥 NUEVO: Serializar los datos de la tabla PrimeraConsulta
                primera_consulta_data = PrimeraConsultaSerializer(primera_consulta).data
                print(f"🔍 DEBUG: Datos de primera consulta serializados")
                
                # Antecedentes Ginecológicos
                antecedentes_gin = AntecedentesGinecologicos.objects.filter(consulta=primera_consulta)
                antecedentes_ginecologicos_data = AntecedentesGinecologicosSerializer(antecedentes_gin, many=True).data
                print(f"🔍 DEBUG: Encontrados {antecedentes_gin.count()} antecedentes ginecológicos")
                
                # Antecedentes Personales
                antecedentes_pers = AntecedentesPersonales.objects.filter(consulta=primera_consulta)
                antecedentes_personales_data = AntecedentesPersonalesSerializer(antecedentes_pers, many=True).data
                print(f"🔍 DEBUG: Encontrados {antecedentes_pers.count()} antecedentes personales")
                
                # Resultados de Estudios
                resultados = ResultadoEstudio.objects.filter(consulta=primera_consulta)
                resultados_estudios_data = ResultadoEstudioSerializer(resultados, many=True).data
                print(f"🔍 DEBUG: Encontrados {resultados.count()} resultados de estudios")
                
                # Órdenes
                ordenes = Orden.objects.filter(primera_consulta=primera_consulta)
                ordenes_data = OrdenDescargaSerializer(ordenes, many=True).data
                print(f"🔍 DEBUG: Encontradas {ordenes.count()} órdenes")
            else:
                print(f"🔍 DEBUG: Tratamiento sin primera consulta")
            
            # Obtener datos relacionados con segunda consulta
            print(f"🔍 DEBUG: Obteniendo datos de segunda consulta...")
            segunda_consulta_data = None
            
            if tratamiento.segunda_consulta:
                segunda_consulta = tratamiento.segunda_consulta
                print(f"🔍 DEBUG: Tratamiento tiene segunda consulta: {segunda_consulta.id}")
                
                # 🔥 NUEVO: Serializar los datos de la tabla SegundaConsulta
                segunda_consulta_data = SegundaConsultaSerializer(segunda_consulta).data
                print(f"🔍 DEBUG: Datos de segunda consulta serializados")
            else:
                print(f"🔍 DEBUG: Tratamiento sin segunda consulta")

            # ==========================================
            # 4. MONITOREOS - Del tratamiento
            # ==========================================
            print(f"\n📊 Buscando monitoreos del tratamiento...")
            from Monitoreo.models import Monitoreo
            from Monitoreo.serializers import MonitoreoSerializer
            
            monitoreos = Monitoreo.objects.filter(
                tratamiento=tratamiento,
                atendido=True
            ).order_by('fecha_realizado')
            print(f"📊 Monitoreos encontrados: {monitoreos.count()}")
            monitoreos_data = MonitoreoSerializer(monitoreos, many=True).data
            
            # Nota: Quitado el retorno temprano. Siempre se agregan datos disponibles.
            
            # ==========================================
            # 5. TRANSFERENCIAS - Del tratamiento
            # ==========================================
            print(f"\n📊 Buscando transferencias del tratamiento...")
            from Transferencia.models import Transferencia
            from Transferencia.serializers import TransferenciaSerializer
            
            transferencias = Transferencia.objects.filter(tratamiento=tratamiento)
            print(f"📊 Transferencias encontradas: {transferencias.count()}")
            transferencias_data = TransferenciaSerializer(transferencias, many=True).data
            
            # ==========================================
            # 6. SEGUIMIENTO - Del tratamiento
            # ==========================================
            print(f"\n📊 Verificando seguimiento del tratamiento...")
            from Seguimiento.models import SeguimientoTratamiento

            seguimiento_qs = SeguimientoTratamiento.objects.filter(
                tratamiento=tratamiento
            )

            tiene_seguimiento = seguimiento_qs.exists()

            seguimiento_finalizado = seguimiento_qs.filter(
                nacido_vivo__isnull=False
            ).exists()

            print(f"📊 Tiene seguimiento: {tiene_seguimiento}")
            print(f"🏁 Seguimiento finalizado: {seguimiento_finalizado}")
            
            # ==========================================
            # 7. PUNCIÓN - Verificar si existe
            # ==========================================
            existe_puncion = tratamiento.puncion is not None or punciones.exists()
            print(f"📊 Existe punción: {existe_puncion}")

            print(f"🔍 DEBUG: Preparando respuesta final...")
            response_data = {
                'tratamiento': tratamiento_data,
                'ovocitos': ovocitos_data,
                'fertilizaciones': fertilizaciones_data,
                'embriones': embriones_data,
                'estado_actual': estado,
                'primera_consulta': primera_consulta_data,
                'segunda_consulta': segunda_consulta_data,
                'antecedentes_ginecologicos': antecedentes_ginecologicos_data,
                'antecedentes_personales': antecedentes_personales_data,
                'resultados_estudios': resultados_estudios_data,
                'ordenes': ordenes_data,
                'monitoreos': monitoreos_data,  # 🔥 NUEVO
                'transferencias': transferencias_data,  # 🔥 NUEVO
                'tiene_seguimiento': tiene_seguimiento,  # 🔥 NUEVO
                "seguimiento_finalizado": seguimiento_finalizado,
                'existe_puncion': existe_puncion,  # 🔥 NUEVO
            }
            print(f"🔍 DEBUG: Respuesta preparada, enviando...")
            print(f"\n✅ RESUMEN FINAL:")
            print(f"   Ovocitos: {len(ovocitos_data)}")
            print(f"   Fertilizaciones: {len(fertilizaciones_data)}")
            print(f"   Embriones: {len(embriones_data)}")
            print(f"   Monitoreos: {len(monitoreos_data)}")
            print(f"   Transferencias: {len(transferencias_data)}")
            print(f"   Seguimiento: {tiene_seguimiento}")
            print(f"   Seguimiento finalizado: {seguimiento_finalizado}")
            print(f"   Punción: {existe_puncion}")
            print(f"{'='*60}\n")
            return Response(response_data, status=status.HTTP_200_OK)

        except Tratamiento.DoesNotExist:
            print(f"🚨 ERROR: Tratamiento con ID {pk} no encontrado")
            return Response({
                "detail": f"Tratamiento con ID {pk} no encontrado.",
                "estado_actual": estado,
                "status": status.HTTP_404_NOT_FOUND,
            })
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
        print(f"🧩 Tratamientos encontrados: {tratamientos.count()}")
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

            paciente = tratamiento.paciente
            usuario = request.user
            ahora = timezone.now()

            # ==========================================
            # ⭐ 1. DESCARTAR OVOCITOS FRESCOS
            # ==========================================
            ovocitos_frescos = Ovocito.objects.filter(
                paciente=paciente,
                tipo_estado=Ovocito.ESTADO_FRESCO
            )

            ovocitos_list = list(ovocitos_frescos)

            ovocitos_frescos.update(
                tipo_estado=Ovocito.ESTADO_DESCARTADO
            )

            # ---- Historial de OVO ----
            for ovocito in ovocitos_list:
                HistorialOvocito.objects.create(
                    ovocito=ovocito,
                    paciente=paciente,
                    estado="descartado",
                    nota=f"Ovocito descartado automáticamente por cancelación del tratamiento #{tratamiento.id}.",
                    usuario=usuario
                )

            # ==========================================
            # ⭐ 2. DESCARTAR EMBRIONES FRESCOS
            # ==========================================
            ovocitos_paciente = Ovocito.objects.filter(paciente=paciente)
            fertilizaciones = Fertilizacion.objects.filter(ovocito__in=ovocitos_paciente)

            embriones_frescos = Embrion.objects.filter(
                fertilizacion__in=fertilizaciones,
                estado__iexact="fresco"
            )

            embriones_list = list(embriones_frescos)

            embriones_frescos.update(
                estado="descartado",
                fecha_baja=ahora,
                causa_descarte="Cancelación del tratamiento"
            )

            # ---- Historial de EMBRIÓN ----
            for emb in embriones_list:
                HistorialEmbrion.objects.create(
                    embrion=emb,
                    paciente=paciente,
                    estado="descartado",
                    calidad=str(emb.calidad) if emb.calidad else None,
                    nota=f"Embrión descartado automáticamente por cancelación del tratamiento #{tratamiento.id}.",
                    observaciones="Descarte automático del embrión",
                    tipo_modificacion="cancelacion_tratamiento",
                    usuario=usuario
                )

            # ==========================================
            # ⭐ 3. CANCELAR TRATAMIENTO
            # ==========================================
            tratamiento.activo = False
            tratamiento.motivo_finalizacion = motivo
            tratamiento.save(update_fields=["activo", "motivo_finalizacion"])

            # ==========================================
            # ⭐ 4. RESPUESTA FINAL
            # ==========================================
            return Response(
                {
                    "success": True,
                    "message": "Tratamiento cancelado y gametos descartados correctamente.",
                    "ovocitos_descartados": len(ovocitos_list),
                    "embriones_descartados": len(embriones_list),
                },
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

    @action(detail=False, methods=['get'], url_path=r'estado/(?P<paciente_id>\d+)')
    def estado_actual_trat_activos(self, request, paciente_id=None):
        """
        Devuelve el estado actual del único tratamiento activo del paciente especificado.
        Un paciente solo puede tener un tratamiento activo a la vez.
        Ejemplo: /api/tratamientos/estado/123/
        """
        print(f"🧩 Buscando estado actual del tratamiento activo para paciente_id={paciente_id}")
        
        # Buscar el tratamiento activo del paciente (solo debería haber uno)
        tratamiento_activo = (
            Tratamiento.objects
            .select_related('paciente', 'medico', 'primera_consulta', 'segunda_consulta', 'puncion', 'transferencia')
            .prefetch_related('lista_monitoreos')
            .filter(paciente_id=paciente_id, activo=True)
            .first()
        )

        if not tratamiento_activo:
            return Response(
                {
                    "paciente_id": paciente_id, 
                    "estado_actual": None,
                    "message": "No se encontró tratamiento activo para este paciente"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Usar el método estado_actual del modelo (invocar correctamente)
        estado = tratamiento_activo.estado_actual()
        print(f"🧩 Estado encontrado: {estado}")

        return Response(
            {
                "paciente_id": paciente_id, 
                "tratamiento_id": tratamiento_activo.id,
                "estado_actual": estado
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='filtrar_estado', url_name='filtrar_estado')
    def filtrar_pacientes_por_estado(self, request):
        """
        Filtra pacientes que tienen tratamientos activos con un estado específico.
        
        POST /api/tratamientos/filtrar_estado/
        
        Body JSON:
        {
            "estado": "Monitoreos finalizados",
            "pacientes_ids": [1, 2, 3, 4, 5]
        }
        
        Respuesta:
        {
            "estado_buscado": "Monitoreos finalizados",
            "pacientes_que_cumplen": [
                {
                    "paciente_id": 2,
                    "tratamiento_id": 15,
                    "estado_actual": "Monitoreos finalizados"
                },
                {
                    "paciente_id": 4,
                    "tratamiento_id": 23,
                    "estado_actual": "Monitoreos finalizados"
                }
            ],
            "total_encontrados": 2,
            "total_revisados": 5
        }
        """
        try:
            # Validar datos de entrada
            estado_buscado = request.data.get('estado', '').strip()
            pacientes_ids = request.data.get('pacientes_ids', [])
            
            if not estado_buscado:
                return Response(
                    {"error": "El campo 'estado' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(pacientes_ids, list) or not pacientes_ids:
                return Response(
                    {"error": "El campo 'pacientes_ids' debe ser un array no vacío"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que todos los elementos sean enteros
            try:
                pacientes_ids = [int(pid) for pid in pacientes_ids]
            except (ValueError, TypeError):
                return Response(
                    {"error": "Todos los elementos en 'pacientes_ids' deben ser números enteros"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🔍 Buscando pacientes con estado '{estado_buscado}' entre IDs: {pacientes_ids}")
            
            # Buscar tratamientos activos de los pacientes especificados
            tratamientos_activos = (
                Tratamiento.objects
                .select_related('paciente', 'medico', 'primera_consulta', 'segunda_consulta', 'puncion', 'transferencia')
                .prefetch_related('lista_monitoreos')
                .filter(paciente_id__in=pacientes_ids, activo=True)
            )
            
            pacientes_que_cumplen = []
            
            # Evaluar el estado de cada tratamiento
            for tratamiento in tratamientos_activos:
                estado_actual = tratamiento.estado_actual
                print(f"  📋 Paciente {tratamiento.paciente_id} - Tratamiento {tratamiento.id} - Estado: '{estado_actual}'")
                
                if estado_actual == estado_buscado:
                    pacientes_que_cumplen.append({
                        "paciente_id": tratamiento.paciente_id,
                        "tratamiento_id": tratamiento.id,
                        "estado_actual": estado_actual
                    })
            
            print(f"✅ Encontrados {len(pacientes_que_cumplen)} pacientes que cumplen el criterio")
            
            return Response({
                "estado_buscado": estado_buscado,
                "pacientes_que_cumplen": pacientes_que_cumplen,
                "total_encontrados": len(pacientes_que_cumplen),
                "total_revisados": len(pacientes_ids)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🚨 ERROR en filtrar_pacientes_por_estado: {str(e)}")
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='filtrar_estados', url_name='filtrar_estados')
    def filtrar_pacientes_por_estados(self, request):
        """
        Filtra pacientes con tratamientos activos cuyo estado_actual coincide con cualquiera
        de los estados provistos.

        POST /api/tratamientos/filtrar_estados/

        Body JSON:
        {
            "estados": ["Fertilización", "Punción", "Transferencia", "Finalizado"],
            "pacientes_ids": [1, 2, 3, 4, 5]
        }

        Respuesta:
        {
            "estados_buscados": ["Fertilización", "Punción", "Transferencia", "Finalizado"],
            "pacientes_que_cumplen": [
                {"paciente_id": 2, "tratamiento_id": 15, "estado_actual": "Punción"}
            ],
            "total_encontrados": 1,
            "total_revisados": 5
        }
        """
        try:
            estados_buscados = request.data.get('estados', None)
            pacientes_ids = request.data.get('pacientes_ids', [])

            if not isinstance(estados_buscados, list) or not estados_buscados:
                return Response(
                    {"error": "'estados' debe ser una lista no vacía de strings."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            estados_lista = [str(e).strip() for e in estados_buscados if str(e).strip()]
            if not estados_lista:
                return Response(
                    {"error": "'estados' no contiene valores válidos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not isinstance(pacientes_ids, list) or not pacientes_ids:
                return Response(
                    {"error": "'pacientes_ids' debe ser una lista no vacía."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                pacientes_ids = [int(x) for x in pacientes_ids]
            except (ValueError, TypeError):
                return Response(
                    {"error": "'pacientes_ids' debe contener enteros válidos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tratamientos_activos = (
                Tratamiento.objects
                .select_related('paciente', 'medico', 'primera_consulta', 'segunda_consulta', 'puncion', 'transferencia')
                .prefetch_related('lista_monitoreos')
                .filter(paciente_id__in=pacientes_ids, activo=True)
            )

            pacientes_ids_que_cumplen = []
            
            for tratamiento in tratamientos_activos:
                estado_actual = tratamiento.estado_actual
                print(f"  📋 Paciente {tratamiento.paciente_id} - Tratamiento {tratamiento.id} - Estado: '{estado_actual}'")
                if estado_actual in estados_lista:
                    pacientes_ids_que_cumplen.append(tratamiento.paciente_id)
            
            # Obtener los pacientes completos con sus datos
            pacientes_obj = CustomUser.objects.filter(id__in=pacientes_ids_que_cumplen)
            pacientes_que_cumplen = CustomUserSerializer(pacientes_obj, many=True).data
            
            return Response({
                "estados_buscados": estados_lista,
                "pacientes_que_cumplen": pacientes_que_cumplen,
                "total_encontrados": len(pacientes_que_cumplen),
                "total_revisados": len(pacientes_ids)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"🚨 ERROR en filtrar_pacientes_por_estados: {str(e)}")
            import traceback
            print(f"🚨 TRACEBACK: {traceback.format_exc()}")
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path=r'tiene-tratamientos-activos/(?P<medico_id>\d+)')
    def tiene_tratamientos_activos(self, request, medico_id=None):
        """
        Devuelve true si el médico tiene al menos un tratamiento activo.
        GET /api/tratamientos/tiene-tratamientos-activos/<medico_id>/
        """
        existe = Tratamiento.objects.filter(medico_id=medico_id, activo=True).exists()
        return Response({'tiene_tratamientos_activos': existe})