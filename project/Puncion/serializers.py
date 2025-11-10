from rest_framework import serializers
from .models import Puncion

class PuncionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Puncion
		fields = '__all__'
