# Orden/serializers.py

from rest_framework import serializers
from .models import Orden

class OrdenDescargaSerializer(serializers.ModelSerializer):
    """Serializador para exponer las órdenes con la URL de descarga."""
    
    # Nota: Si el frontend espera 'fecha' en lugar de 'fecha_creacion', 
    # puedes añadir un campo personalizado aquí, pero usaremos el nombre del modelo.
    
    class Meta:
        model = Orden
        fields = ['id', 'fecha_creacion', 'tipo_estudio', 'pdf_url']