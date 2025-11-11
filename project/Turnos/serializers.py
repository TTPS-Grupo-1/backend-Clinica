# Turnos/serializers.py

from rest_framework import serializers
from .models import Turno
from CustomUser.models import CustomUser # 👈 Usamos CustomUser

class TurnoSerializer(serializers.ModelSerializer):
    # 1. Campo Médico (Acepta 'medico' minúscula del JSON, mapea a FK 'Medico' mayúscula)
    medico = serializers.PrimaryKeyRelatedField(
        source='Medico', 
        queryset=CustomUser.objects.filter(rol='MEDICO') 
    )

    # 2. Campo Paciente (Acepta 'Paciente' o 'paciente' del JSON, mapea a FK 'Paciente' mayúscula)
    Paciente = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(rol='PACIENTE') 
    )

    class Meta:
        model = Turno
        # ✅ CAMPOS AGREGADOS: cancelado, atendido, y es_monitoreo
        fields = [
            'id', 
            'medico',           
            'Paciente',         
            'fecha_hora',       
            'id_externo',       
            'cancelado',        
            'atendido',         
            'es_monitoreo',     
            'created_at',       
        ]
