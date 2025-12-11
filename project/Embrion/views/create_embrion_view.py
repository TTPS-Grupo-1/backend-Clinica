
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from Embrion.models import Embrion
from Embrion.serializers import EmbrionSerializer
import logging

logger = logging.getLogger(__name__)

class CreateEmbrionMixin:
	"""
	Mixin para crear un embrión en un ViewSet.
	"""
	# No need to override create() since it's already properly handled in EmbrionViewSet
	pass

class UpdateEmbrionMixin:
	"""
	Mixin para actualizar un embrión en un ViewSet.
	"""
	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		print(request.data)
		if not serializer.is_valid():
			logger.warning(f"Errores de validación: {serializer.errors}")
			return Response({
				"success": False,
				"message": "Hay errores en los campos ingresados.",
				"errors": serializer.errors
			}, status=status.HTTP_400_BAD_REQUEST)
		try:
			with transaction.atomic():
				embrion = serializer.save()
				logger.info(f"Embrion actualizado: {embrion}")
				return Response({
					"success": True,
					"message": "Embrion actualizado correctamente.",
					"data": serializer.data
				}, status=status.HTTP_200_OK)
		except IntegrityError as e:
			logger.error(f"Error de integridad: {str(e)}")
			return Response({
				"success": False,
				"message": "Error de integridad al actualizar el embrión."
			}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.exception("Error inesperado al actualizar embrión.")
			return Response({
				"success": False,
				"message": "Ocurrió un error al actualizar el embrión."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	def partial_update(self, request, *args, **kwargs):
		kwargs['partial'] = True
		return self.update(request, *args, **kwargs)
