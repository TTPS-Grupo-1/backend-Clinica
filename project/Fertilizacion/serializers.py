from rest_framework import serializers
from .models import Fertilizacion

class FertilizacionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fertilizacion
		fields = '__all__'