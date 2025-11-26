from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from Ovocito.models import Ovocito
from Ovocito.serializers import OvocitoSerializer
import logging
import requests
import json

logger = logging.getLogger(__name__)

class CreatePuncionMixin:

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

                ovocitos_data = request.data.get("ovocitos", [])
                ovocitos_creados = []
                asignaciones = []  # ← para devolver todo al frontend

                for ov_data in ovocitos_data:
                    ov_data["puncion"] = puncion.id

                    ov_serializer = OvocitoSerializer(data=ov_data)
                    if ov_serializer.is_valid():
                        ovocito = ov_serializer.save()
                        logger.info(f"Ovocito creado en punción: {ovocito.identificador}")

                        # -----------------------------------------------
                        # 🔥 ASIGNACIÓN SUPABASE SI CRIOPRESERVADO
                        # -----------------------------------------------
                        if ovocito.tipo_estado == "criopreservado":
                            try:
                                res = requests.post(
                                    "https://ssewaxrnlmnyizqsbzxe.supabase.co/functions/v1/assign-ovocyte",
                                    json={
                                        'nro_grupo': 1,
                                        'ovocito_id': ovocito.identificador
                                    },
                                    headers={'Content-Type': 'application/json'}
                                )

                                logger.info(f"Supabase asignación → {res.status_code} - {res.text}")

                                if res.ok:
                                    data = res.json()

                                    if isinstance(data, list) and len(data) > 0:
                                        asign = data[0]
                                        asignaciones.append(asign)

                                        # guardar en el ovocito
                                        ovocito.tanque_id = asign.get("tanque_id")
                                        ovocito.rack_id = asign.get("rack_id")
                                        ovocito.save()

                                    else:
                                        asignaciones.append({"error": "Respuesta vacía de Supabase"})
                                else:
                                    asignaciones.append({"error": f"Supabase devolvió {res.status_code}"})

                            except Exception as e:
                                logger.error(f"Error asignando ovocito en Supabase: {str(e)}")
                                asignaciones.append({"error": "Error de conexión con Supabase"})

                        # ------------------------------------------------

                        ovocitos_creados.append(ovocito)

                    else:
                        logger.warning(f"Ovocito inválido: {ov_serializer.errors}")

                return Response({
                    "success": True,
                    "message": "Punción registrada correctamente.",
                    "data": serializer.data,
                    "ovocitos": [OvocitoSerializer(o).data for o in ovocitos_creados],
                    "asignaciones": asignaciones  # → te devuelvo todas las asignaciones
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
