from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from Monitoreo.models import Monitoreo
from Monitoreo.serializers import MonitoreoSerializer
import logging

logger = logging.getLogger(__name__)

class CreateMonitoreoMixin(APIView):
	"""
	Vista para crear un monitoreo.
	"""
	def post(self, request):
		serializer = MonitoreoSerializer(data=request.data)
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
				logger.info(f"Monitoreo creado: {monitoreo.id}")
				return Response({
					"success": True,
					"message": "Monitoreo registrado correctamente.",
					"data": serializer.data
				}, status=status.HTTP_201_CREATED)
		except IntegrityError as e:
			logger.error(f"Error de integridad: {str(e)}")
			return Response({
				"success": False,
				"message": "El monitoreo ya existe o hay un campo duplicado."
			}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.exception("Error inesperado al crear monitoreo.")
			return Response({
				"success": False,
				"message": "Ocurrió un error al registrar el monitoreo."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
