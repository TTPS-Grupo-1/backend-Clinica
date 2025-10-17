from rest_framework import viewsets
from ..models import Fertilizacion
from ..serializers import FertilizacionSerializer
import logging

logger = logging.getLogger(__name__)

class FertilizacionViewSet(viewsets.ModelViewSet):
	queryset = Fertilizacion.objects.all()
	serializer_class = FertilizacionSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			logger.warning(f"Errores de validación Fertilización: {serializer.errors}")
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		from rest_framework import status
		from rest_framework.response import Response
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
