from rest_framework import serializers
from .models import PrimeraConsulta


class PrimeraConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimeraConsulta
        fields = '__all__'
