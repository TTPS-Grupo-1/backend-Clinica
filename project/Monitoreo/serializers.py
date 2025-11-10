from rest_framework import serializers
from Monitoreo.models import Monitoreo


class MonitoreoSerializer(serializers.ModelSerializer):
    # ✅ Campos calculados del paciente y médico
    paciente_nombre = serializers.CharField(source='paciente.get_full_name', read_only=True)
    paciente_dni = serializers.IntegerField(source='paciente.dni', read_only=True)
    medico_nombre = serializers.CharField(source='medico.get_full_name', read_only=True)
    medico_dni = serializers.IntegerField(source='medico.dni', read_only=True)
    
    class Meta:
        model = Monitoreo
        fields = [
            'id',
            'descripcion',
            'tratamiento',
            'atendido',
            'fecha_creacion',
            'fecha_atencion',
            'fecha_realizado',
            'paciente_nombre',
            'paciente_dni',
            'medico_nombre',
            'medico_dni',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_realizado']
    
    def validate_descripcion(self, value):
        """Validar que la descripción no esté vacía al atender"""
        if self.instance and self.instance.atendido:
            # Si ya está atendido, no permitir cambios
            raise serializers.ValidationError("No se puede modificar un monitoreo ya atendido")
        return value
