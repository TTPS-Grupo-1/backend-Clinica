import json
import logging
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from ..serializers import SegundaConsultaSerializer
from ..models import SegundaConsulta
from Tratamiento.models import Tratamiento
from Monitoreo.models import Monitoreo
from ResultadoEstudio.models import ResultadoEstudio

logger = logging.getLogger(__name__)

class CreateSegundaConsultaMixin:
    """
    Crea una SegundaConsulta, actualiza los estudios y registra los monitoreos.
    Compatible con tu modelo actual (campos planos y BinaryField para PDF).
    """

    def create(self, request, *args, **kwargs):
        print("📩 Payload recibido:", request.data)

        try:
            with transaction.atomic():
                # ---------- 1️⃣ Parseo de datos del request ----------
                tratamiento_id = request.data.get("tratamiento_id")
                protocolo = json.loads(request.data.get("protocolo", "{}"))
                monitoreos = json.loads(request.data.get("monitoreo", "[]"))
                estudios = json.loads(request.data.get("estudios", "[]"))
                conclusion = json.loads(request.data.get("conclusion", "{}"))
                consentimiento = request.FILES.get("consentimiento")

                # ---------- 2️⃣ Validar tratamiento ----------
                try:
                    tratamiento = Tratamiento.objects.get(id=tratamiento_id)
                except Tratamiento.DoesNotExist:
                    return Response(
                        {"error": f"Tratamiento con id {tratamiento_id} no encontrado"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # ---------- 3️⃣ Crear la segunda consulta ----------
                segunda_data = {
                    "droga": protocolo.get("droga"),
                    "tipo_medicacion": protocolo.get("tipo"),
                    "dosis_medicacion": protocolo.get("dosis"),
                    "duracion_medicacion": protocolo.get("duracion"),
                    "ovocito_viable": conclusion.get("ovocitoViable", False),
                    "semen_viable": conclusion.get("semenViable", False),
                }

                if consentimiento:
                    segunda_data["consentimiento_informado"] = consentimiento
                
                segunda_serializer = SegundaConsultaSerializer(data=segunda_data)
                segunda_serializer.is_valid(raise_exception=True)
                segunda = segunda_serializer.save()

                # ---------- 4️⃣ Asociar al tratamiento ----------
                tratamiento.segunda_consulta = segunda
                tratamiento.save(update_fields=["segunda_consulta"])

                # ---------- 5️⃣ Crear Monitoreos ----------
                for fecha in monitoreos:
                    Monitoreo.objects.create(
                        tratamiento=tratamiento,
                        fecha_atencion=fecha,
                        descripcion="Monitoreo programado desde segunda consulta"
                    )

                # ---------- 6️⃣ Actualizar Resultados de Estudios ----------
                for est in estudios:
                    try:
                        resultado = ResultadoEstudio.objects.get(id=est["id"])
                        resultado.valor = est.get("valor")
                        resultado.save()
                    except ResultadoEstudio.DoesNotExist:
                        logger.warning(f"Estudio ID {est.get('id')} no encontrado")

                # ---------- 7️⃣ Respuesta ----------
                response_data = {
                    "success": True,
                    "message": "Segunda consulta creada exitosamente",
                    "segunda_consulta": segunda_serializer.data,
                    "monitoreos_creados": len(monitoreos),
                    "estudios_actualizados": len(estudios),
                }

                logger.info(f"✅ SegundaConsulta creada: ID {segunda.id}")
                return Response(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"❌ Error de integridad: {e}")
            return Response(
                {"error": "Error de integridad en base de datos", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return Response(
                {"error": "Error interno del servidor", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
