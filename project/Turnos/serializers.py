from rest_framework import serializers
from Turnos.models import Turno
from Medicos.models import Medico


class TurnoSerializer(serializers.ModelSerializer):
    
    # Campo Medico (Se mantiene igual, la validación del médico es necesaria)
    medico = serializers.PrimaryKeyRelatedField(
        queryset=Medico.objects.all(),
    )

    Paciente = serializers.IntegerField() 

    class Meta:
        model = Turno
        # El campo debe seguir la capitalización del modelo
        fields = [
            'medico',
            'Paciente', 
            'fecha_hora'
        ]
        # Indicamos a DRF que 'Paciente' no debe ser manejado como una relación
        extra_kwargs = {
            'Paciente': {'required': True}
        }