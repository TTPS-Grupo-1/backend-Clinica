from rest_framework import serializers
from .models import Fertilizacion
from Ovocito.models import Ovocito
import logging

logger = logging.getLogger(__name__)

class FertilizacionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fertilizacion
		fields = '__all__'
	
	def to_internal_value(self, data):
		"""
		Interceptar ANTES de la validación de Django.
		Si viene ovocito_donado_id, eliminar el campo ovocito del payload.
		"""
		# Hacer una copia para no modificar el original
		data = data.copy() if hasattr(data, 'copy') else dict(data)
		
		# Si viene ovocito_donado_id, es un ovocito donado
		if 'ovocito_donado_id' in data and data.get('ovocito_donado_id'):
			logger.info(f"🏦 Detectado ovocito donado en payload: {data.get('ovocito_donado_id')}")
			# Eliminar ovocito del payload para evitar validación de FK
			if 'ovocito' in data:
				logger.info(f"🗑️ Eliminando campo 'ovocito' del payload (usando donado)")
				data.pop('ovocito')
		
		return super().to_internal_value(data)