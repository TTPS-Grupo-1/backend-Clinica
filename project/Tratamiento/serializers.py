from rest_framework import serializers
from .models import Tratamiento
from CustomUser.models import CustomUser


class TratamientoSerializer(serializers.ModelSerializer):
  #  paciente_nombre = serializers.SerializerMethodField()
   # medico_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Tratamiento
        fields = [
            'id', 'fecha_inicio', 
            'paciente', 'medico', 'medico',
            'activo', 'fecha_creacion', 'fecha_modificacion', 'primera_consulta',
            'segunda_consulta', 'transferencia', 'puncion', 'monitoreos', 'turnos'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_paciente_nombre(self, obj):
        return obj.paciente.get_full_name() or obj.paciente.username
    
    def get_medico_nombre(self, obj):
        return obj.medico.get_full_name() or obj.medico.username


class TratamientoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tratamientos con validaciones específicas"""
    
    class Meta:
        model = Tratamiento
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'paciente', 'medico', 'activo']
    
    def validate_paciente(self, value):
        if value.rol != 'paciente':
            raise serializers.ValidationError("El usuario seleccionado debe tener rol de paciente.")
        return value
    
    def validate_medico(self, value):
        if value.rol != 'medico':
            raise serializers.ValidationError("El usuario seleccionado debe tener rol de médico.")
        return value