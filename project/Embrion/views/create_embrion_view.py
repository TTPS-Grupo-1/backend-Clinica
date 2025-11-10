
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from Embrion.models import Embrion
from Embrion.serializers import EmbrionSerializer
import logging

logger = logging.getLogger(__name__)

class CreateEmbrionMixin(APIView):
	"""
	Vista para crear un embrión.
	"""
	def post(self, request):
		serializer = EmbrionSerializer(data=request.data)
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
				logger.info(f"Embrion creado: {embrion.identificador}")
				return Response({
					"success": True,
					"message": "Embrion registrado correctamente.",
					"data": serializer.data
				}, status=status.HTTP_201_CREATED)
		except IntegrityError as e:
			logger.error(f"Error de integridad: {str(e)}")
			return Response({
				"success": False,
				"message": "El embrión ya existe o hay un campo duplicado."
			}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.exception("Error inesperado al crear embrión.")
			return Response({
				"success": False,
				"message": "Ocurrió un error al registrar el embrión."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateEmbrionMixin(APIView):
	"""
	Vista para actualizar un embrión.
	"""
	def put(self, request, pk):
		try:
			embrion = Embrion.objects.get(pk=pk)
		except Embrion.DoesNotExist:
			return Response({
				"success": False,
				"message": "El embrión no existe."
			}, status=status.HTTP_404_NOT_FOUND)
		serializer = EmbrionSerializer(embrion, data=request.data, partial=True)
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
