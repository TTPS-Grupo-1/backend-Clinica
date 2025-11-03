from rest_framework import serializers
from .models import ResultadoEstudio

class ResultadoEstudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoEstudio
        fields = [
            'id',
            'consulta',
            'nombre_estudio',
            'tipo_estudio',
            'valor',
            'persona',  # si agregaste este campo al modelo
        ]
