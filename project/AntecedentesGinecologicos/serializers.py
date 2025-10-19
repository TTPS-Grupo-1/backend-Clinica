from rest_framework import serializers
from .models import AntecedentesGinecologicos


class AntecedentesGinecologicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentesGinecologicos
        fields = '__all__'

