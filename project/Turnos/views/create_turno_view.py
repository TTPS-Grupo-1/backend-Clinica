from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging
from datetime import datetime

# ⚠️ Asegúrate de que estas importaciones sean correctas
from Turnos.models import Turno
from Medicos.models import Medico
from Paciente.models import Paciente # <--- ¡IMPORTACIÓN CLAVE!

logger = logging.getLogger(__name__)

class CreateTurnoMixin:
    """
    Mixin para manejar la creación de turnos.
    Asegura la conversión de DNI/ID a instancias de objeto para las claves foráneas.
    """

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            # print(f"Datos recibidos en el backend: {data}") # Se mantiene para diagnóstico

            # --- 1. VALIDACIÓN DE EXISTENCIA Y OBTENCIÓN DE DATOS ---
            required_fields = ['medico', 'paciente', 'fecha', 'hora']
            for field in required_fields:
                if not data.get(field):
                     return Response({
                        "success": False,
                        "message": f"Falta el campo requerido: {field}."
                    }, status=status.HTTP_400_BAD_REQUEST)

            dni_medico_value = data.get('medico')
            paciente_id = data.get('paciente') # Obtiene el valor 1 (minúscula)

            # --- 2. BÚSQUEDA DEL PACIENTE POR ID (Necesaria para obtener la instancia) ---
            try:
                paciente_obj = Paciente.objects.get(id=paciente_id)
            except Paciente.DoesNotExist:
                return Response({
                    "success": False,
                    "message": f"El paciente con ID {paciente_id} especificado no existe."
                }, status=status.HTTP_404_NOT_FOUND)

            # --- 3. BÚSQUEDA DEL MÉDICO POR DNI (PK) ---
            try:
                medico_obj = Medico.objects.get(dni=dni_medico_value) 
            except Medico.DoesNotExist:
                return Response({
                    "success": False,
                    "message": f"El médico con DNI {dni_medico_value} especificado no existe."
                }, status=status.HTTP_404_NOT_FOUND)
            
            # --- 4. COMBINACIÓN DE FECHA, HORA Y VALIDACIÓN DE TIEMPO ---
            try:
                fecha_parte = datetime.strptime(data['fecha'], "%Y-%m-%d").date()
                hora_parte = datetime.strptime(data['hora'], "%H:%M").time()
                fecha_hora_turno = timezone.make_aware(datetime.combine(fecha_parte, hora_parte))
            except ValueError:
                return Response({"success": False, "message": "Formato de fecha u hora inválido. Use YYYY-MM-DD y HH:MM."}, status=status.HTTP_400_BAD_REQUEST)

            if fecha_hora_turno < timezone.now():
                return Response({"success": False, "message": "No se puede crear un turno en una fecha u hora pasada."}, status=status.HTTP_400_BAD_REQUEST)
            
            # --- 5. PREPARACIÓN FINAL DE DATOS PARA EL SERIALIZER ---
            
            # El Serializer de DRF acepta el OBJETO para claves foráneas.
            data['Paciente'] = paciente_obj 
            
            # El Serializer acepta el valor PK para PrimaryKeyRelatedField (el DNI)
            data['medico'] = medico_obj.dni 
            
            # Asignar la fecha combinada
            data['fecha_hora'] = fecha_hora_turno 
            
            # Limpiar campos que no van al Serializer
            if 'paciente' in data:
                del data['paciente'] # Eliminar el ID en minúsculas
            del data['fecha']
            del data['hora']
            
            # --- 6. SERIALIZAR Y GUARDAR ---
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.warning(f"Errores de validación: {serializer.errors}")
                return Response({
                    "success": False,
                    "message": "Hay errores en los campos ingresados.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            turno = serializer.save()
            logger.info(f"Turno creado correctamente: {turno.id}")

            return Response({
                "success": True,
                "message": "Turno registrado correctamente.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(f"Error inesperado al crear turno: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error al crear turno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        