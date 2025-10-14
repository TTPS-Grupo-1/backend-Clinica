from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from Ovocito.models import Ovocito
from Ovocito.serializers import OvocitoSerializer
import logging

logger = logging.getLogger(__name__)

class CreatePuncionMixin:
	"""
	Mixin para manejar la creación de punciones con mensajes personalizados y registro de ovocitos asociados.
	"""

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)

		# Validaciones del serializer
		if not serializer.is_valid():
			logger.warning(f"Errores de validación: {serializer.errors}")
			return Response({
				"success": False,
				"message": "Hay errores en los campos ingresados.",
				"errors": serializer.errors
			}, status=status.HTTP_400_BAD_REQUEST)

		try:
			with transaction.atomic():
				puncion = serializer.save()
				logger.info(f"Punción creada: {puncion}")

				# Si vienen ovocitos en el payload, registrarlos asociados a la punción
				ovocitos_data = request.data.get("ovocitos", [])
				ovocitos_creados = []
				for ov_data in ovocitos_data:
					ov_data["puncion"] = puncion.id
					ov_serializer = OvocitoSerializer(data=ov_data)
					if ov_serializer.is_valid():
						ovocito = ov_serializer.save()
						ovocitos_creados.append(ovocito)
					else:
						logger.warning(f"Ovocito inválido: {ov_serializer.errors}")
				return Response({
					"success": True,
					"message": "Punción registrada correctamente.",
					"data": serializer.data,
					"ovocitos": [OvocitoSerializer(o).data for o in ovocitos_creados]
				}, status=status.HTTP_201_CREATED)

		except IntegrityError as e:
			logger.error(f"Error de integridad: {str(e)}")
			return Response({
				"success": False,
				"message": "La punción ya existe o hay un campo duplicado."
			}, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logger.exception("Error inesperado al crear punción.")
			return Response({
				"success": False,
				"message": "Ocurrió un error al registrar la punción."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
