from rest_framework import serializers
from .models import SegundaConsulta


class SegundaConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegundaConsulta
        fields = [
            'id',
            'primera_consulta',
            'ovocito_viable',
            'semen_viable',
            'consentimiento_informado',
            'tipo_medicacion',
            'dosis_medicacion',
            'duracion_medicacion',
            'fecha',
        ]
        read_only_fields = ['id', 'fecha']