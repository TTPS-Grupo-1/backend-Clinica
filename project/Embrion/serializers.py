from rest_framework import serializers
from .models import Embrion

class EmbrionSerializer(serializers.ModelSerializer):
    paciente_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Embrion
        fields = '__all__'

    def get_paciente_id(self, obj):
        if obj.fertilizacion and obj.fertilizacion.ovocito:
            return obj.fertilizacion.ovocito.paciente.id if obj.fertilizacion.ovocito.paciente else None
        return None