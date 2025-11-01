from rest_framework import serializers
from .models import Monitoreo
from datetime import datetime

class MonitoreoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura calculados desde el tratamiento
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
            'atendido',
            'fecha_creacion',
            'fecha_atencion',  # ✅ Ahora es un campo editable
            'paciente_nombre',
            'paciente_dni',
            'medico_nombre',
            'medico_dni',
        ]
        read_only_fields = [
            'fecha_creacion',
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
        
        # Validar que el tratamiento exista
        if 'tratamiento' in attrs:
            if not attrs['tratamiento']:
                raise serializers.ValidationError({
                    'tratamiento': 'El tratamiento es requerido'
                })
        
        # ✅ NUEVO: Validar fecha de atención si se proporciona
        if 'fecha_atencion' in attrs and attrs['fecha_atencion']:
            fecha_atencion = attrs['fecha_atencion']
            
            # Validar que la fecha de atención no sea en el pasado
            if fecha_atencion < datetime.now(fecha_atencion.tzinfo):
                raise serializers.ValidationError({
                    'fecha_atencion': 'La fecha de atención no puede ser en el pasado'
                })
        
        return attrs
    
    def to_representation(self, instance):
        """
        Personaliza la salida JSON para incluir datos del tratamiento
        """
        representation = super().to_representation(instance)
        
        # Agregar información adicional del tratamiento
        if instance.tratamiento:
            representation['tratamiento_info'] = {
                'id': instance.tratamiento.id,
                'fecha_inicio': instance.tratamiento.fecha_inicio,
                'activo': instance.tratamiento.activo,
            }
        
        # ✅ Agregar indicador si ya pasó la fecha de atención
        if instance.fecha_atencion:
            representation['fecha_atencion_pasada'] = instance.fecha_atencion < datetime.now(instance.fecha_atencion.tzinfo)
        
        return representation
