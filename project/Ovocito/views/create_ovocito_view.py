from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
import logging
import requests
import json

logger = logging.getLogger(__name__)

class CreateOvocitoMixin:

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
            print("Datos validados, creando ovocito...")
            print("sdaifdsifsifndsjfsdjfndshfbs")
            ovocito = serializer.save()

            # Si está criopreservado → llamar Supabase
            asignacion = None
            if ovocito.tipo_estado == 'criopreservado':

                res = requests.post(
                    'https://ssewaxrnlmnyizqsbzxe.supabase.co/functions/v1/assign-ovocyte',
                    json={
                        'nro_grupo': 1,
                        'ovocito_id': ovocito.identificador
                    },
                    headers={'Content-Type': 'application/json'}
                )
                print("supaaaaaaa")
                print(f"Respuesta Supabase: {res.status_code} - {res.text}")    
                print(f"Respuesta Supabase: {res.status_code} - {res.text}")
                logger.info(f"Respuesta Supabase: {res.status_code} - {res.text}")

                if res.ok:
                    data = res.json()

                    # Si la función devuelve una lista con un objeto
                    if isinstance(data, list) and len(data) > 0:
                        asignacion = data[0]

                        # Guardamos tanque y rack
                        ovocito.tanque_id = asignacion.get("tanque_id")
                        ovocito.rack_id = asignacion.get("rack_id")
                        ovocito.save()

            logger.info(f"Ovocito creado: {ovocito.identificador}")

            return Response({
                "success": True,
                "message": "Ovocito registrado correctamente.",
                "data": serializer.data,
                "asignacion": asignacion
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            return Response({
                "success": False,
                "message": "El ovocito ya existe o hay un campo duplicado."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Error inesperado al crear ovocito.")
            return Response({
                "success": False,
                "message": "Ocurrió un error al registrar el ovocito."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
