from rest_framework import serializers
from .models import Ovocito
from datetime import date
import re

class OvocitoSerializer(serializers.ModelSerializer):
    fue_criopreservado = serializers.SerializerMethodField()

    class Meta:
        model = Ovocito
        fields = '__all__'
    
    def get_fue_criopreservado(self, obj):
        """
        Verifica si el ovocito alguna vez fue criopreservado consultando su historial.
        """
        from Historial_ovocito.models import HistorialOvocito
        
        # Verificar si el estado actual es criopreservado
        if obj.tipo_estado == 'criopreservado':
            return True
        
        # Verificar en el historial si alguna vez estuvo criopreservado
        return HistorialOvocito.objects.filter(
            ovocito=obj,
            estado='criopreservado'
        ).exists()

        
  