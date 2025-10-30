from rest_framework import serializers
from .models import Monitoreo

class MonitoreoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Monitoreo
		fields = '__all__'
