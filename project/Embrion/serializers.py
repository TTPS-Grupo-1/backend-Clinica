from rest_framework import serializers
from .models import Embrion

class EmbrionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Embrion
		fields = '__all__'
