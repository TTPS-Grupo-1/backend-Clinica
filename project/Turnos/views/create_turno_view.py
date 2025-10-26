from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging
from datetime import datetime

# ⚠️ La importación CLAVE: Usamos CustomUser en lugar de Medico/Paciente
from Turnos.models import Turno 
from CustomUser.models import CustomUser 

logger = logging.getLogger(__name__)

class CreateTurnoMixin:
    """
    MixIn para manejar la creación de turnos.
    Busca Médicos y Pacientes dentro del modelo CustomUser por DNI/ID y rol.
    """

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            # print(f"Datos recibidos en el backend: {data}") # Mantener para diagnóstico

            # --- 1. VALIDACIÓN DE EXISTENCIA ---
            required_fields = ['medico', 'paciente', 'fecha', 'hora']
            for field in required_fields:
                if not data.get(field):
                     return Response({
                        "success": False,
                        "message": f"Falta el campo requerido: {field}."
                    }, status=status.HTTP_400_BAD_REQUEST)

            dni_medico_value = data.get('medico')
            paciente_id = data.get('paciente') 
            
            # --- 2. BÚSQUEDA DEL PACIENTE POR ID Y ROL ---
            try:
                # Busca por ID y verifica el ROL
                paciente_obj = CustomUser.objects.get(id=paciente_id, rol='PACIENTE')
            except CustomUser.DoesNotExist:
                return Response({
                    "success": False,
                    "message": f"El paciente (ID: {paciente_id}) no existe o no tiene rol PACIENTE."
                }, status=status.HTTP_404_NOT_FOUND)

            # --- 3. BÚSQUEDA DEL MÉDICO POR DNI Y ROL ---
            try:
                # Busca por DNI y verifica el ROL
                medico_obj = CustomUser.objects.get(dni=dni_medico_value, rol='MEDICO') 
            except CustomUser.DoesNotExist:
                return Response({
                    "success": False,
                    "message": f"El médico (DNI: {dni_medico_value}) no existe o no tiene rol MEDICO."
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
            
            # Asignar la instancia del objeto a la clave 'Paciente' (MAYÚSCULA)
            data['Paciente'] = paciente_obj 
            
            # Asignar la PK del médico (el DNI) a la clave 'medico' (MINÚSCULA)
            data['medico'] = medico_obj.dni 
            
            # Asignar la fecha combinada
            data['fecha_hora'] = fecha_hora_turno 
            
            # Limpiar campos originales (minúsculas)
            if 'paciente' in data: del data['paciente'] 
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