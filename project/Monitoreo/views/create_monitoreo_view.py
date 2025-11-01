from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView  # 👈 Agrega esta importación
import logging
from django.db import IntegrityError, transaction
from Monitoreo.models import Monitoreo
from Monitoreo.serializers import MonitoreoSerializer

logger = logging.getLogger(__name__)

class CreateMonitoreoMixin:
	"""
	Mixin para personalizar la creación de monitoreos
	"""
	
	def perform_create(self, serializer):
		"""
		Lógica adicional al crear un monitoreo
		"""
		logger.info(f"📝 Creando nuevo monitoreo...")
		
		monitoreo = serializer.save()
		
		# TODO: Cuando exista Tratamiento, puedes agregar notificaciones
		# if monitoreo.tratamiento and monitoreo.medico:
		#     enviar_notificacion_medico(monitoreo.medico, monitoreo)
		
		logger.info(f"✅ Monitoreo {monitoreo.id} creado exitosamente")
		
		return monitoreo


class UpdateMonitoreoMixin(APIView):
	"""
	Vista para actualizar un monitoreo.
	"""
	def put(self, request, pk):
		try:
			monitoreo = Monitoreo.objects.get(pk=pk)
		except Monitoreo.DoesNotExist:
			return Response({
				"success": False,
				"message": "El monitoreo no existe."
			}, status=status.HTTP_404_NOT_FOUND)
		serializer = MonitoreoSerializer(monitoreo, data=request.data, partial=True)
		if not serializer.is_valid():
			logger.warning(f"Errores de validación: {serializer.errors}")
			return Response({
				"success": False,
				"message": "Hay errores en los campos ingresados.",
				"errors": serializer.errors
			}, status=status.HTTP_400_BAD_REQUEST)
		try:
			with transaction.atomic():
				monitoreo = serializer.save()
				logger.info(f"Monitoreo actualizado: {monitoreo.id}")
				return Response({
					"success": True,
					"message": "Monitoreo actualizado correctamente.",
					"data": serializer.data
				}, status=status.HTTP_200_OK)
		except IntegrityError as e:
			logger.error(f"Error de integridad: {str(e)}")
			return Response({
				"success": False,
				"message": "Error de integridad al actualizar el monitoreo."
			}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.exception("Error inesperado al actualizar monitoreo.")
			return Response({
				"success": False,
				"message": "Ocurrió un error al actualizar el monitoreo."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
