from rest_framework import serializers
from .models import Monitoreo

class MonitoreoSerializer(serializers.ModelSerializer):
    # 👇 Campos de solo lectura para mostrar info del tratamiento
    paciente_nombre = serializers.SerializerMethodField(read_only=True)
    paciente_dni = serializers.SerializerMethodField(read_only=True)
    medico_nombre = serializers.SerializerMethodField(read_only=True)
    medico_dni = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Monitoreo
        fields = [
            'id',
            'descripcion',
            'tratamiento',
            'fecha_creacion',
            'fecha_atencion',
            'atendido',
            'paciente_nombre',  # Campo calculado
            'paciente_dni',     # Campo calculado
            'medico_nombre',    # Campo calculado
            'medico_dni',       # Campo calculado
        ]
        read_only_fields = [
            'fecha_creacion', 
            'fecha_atencion',
            'paciente_nombre', 
            'paciente_dni',
            'medico_nombre',
            'medico_dni'
        ]
    
    def get_paciente_nombre(self, obj):
        """Obtiene el nombre completo del paciente desde el tratamiento"""
        if obj.paciente:
            return f"{obj.paciente.first_name} {obj.paciente.last_name}"
        return None
    
    def get_paciente_dni(self, obj):
        """Obtiene el DNI del paciente desde el tratamiento"""
        return obj.paciente.dni if obj.paciente else None
    
    def get_medico_nombre(self, obj):
        """Obtiene el nombre completo del médico desde el tratamiento"""
        if obj.medico:
            return f"{obj.medico.first_name} {obj.medico.last_name}"
        return None
    
    def get_medico_dni(self, obj):
        """Obtiene el DNI del médico desde el tratamiento"""
        return obj.medico.dni if obj.medico else None
    
    def validate(self, attrs):
        """
        Validación personalizada
        """
        # Validar que la descripción no esté vacía
        if 'descripcion' in attrs and not attrs['descripcion'].strip():
            raise serializers.ValidationError({
                'descripcion': 'La descripción no puede estar vacía'
            })
        
        return attrs
