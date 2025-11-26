from datetime import datetime
import json
import logging
import requests
from io import BytesIO
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from ..serializers import SegundaConsultaSerializer
from ..models import SegundaConsulta
from Tratamiento.models import Tratamiento
from Monitoreo.models import Monitoreo
from ResultadoEstudio.models import ResultadoEstudio
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.conf import settings
from Turnos.models import Turno

logger = logging.getLogger(__name__)

SUPABASE_EDGE_URL = "https://srlgceodssgoifgosyoh.supabase.co/functions/v1/generar_orden_medica"  # 🔧 reemplazá con tu URL real
SUPABASE_RESERVAR_URL = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/reservar_turno"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybGdjZW9kc3Nnb2lmZ29zeW9oIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ0NTU3NiwiZXhwIjoyMDc2MDIxNTc2fQ.4KDD7JytM2J8jMxl6WmYyTArThY4Dd8s6ACJZdYMJMY"
SUPABASE_KEY_RESERVAR = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc"
class CreateSegundaConsultaMixin:
    """
    Crea una SegundaConsulta, actualiza los estudios y registra los monitoreos.
    Luego genera la orden médica de la droga llamando a la Edge Function de Supabase.
    """

    def create(self, request, *args, **kwargs):
        print("📩 Payload recibido:", request.data)

        try:
            with transaction.atomic():
                # ---------- 1️⃣ Parseo de datos ----------
                tratamiento_id = request.data.get("tratamiento_id")
                protocolo = json.loads(request.data.get("protocolo", "{}"))
                monitoreos = json.loads(request.data.get("monitoreo", "[]"))
                estudios = json.loads(request.data.get("estudios", "[]"))
                conclusion = json.loads(request.data.get("conclusion", "{}"))
                consentimiento = request.FILES.get("consentimiento")

                # ---------- 2️⃣ Validar tratamiento ----------
                try:
                    tratamiento = Tratamiento.objects.select_related("paciente", "medico").get(id=tratamiento_id)
                except Tratamiento.DoesNotExist:
                    return Response(
                        {"error": f"Tratamiento con id {tratamiento_id} no encontrado"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # ---------- 3️⃣ Crear Segunda Consulta ----------
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
                for item in monitoreos:
                    # Si el frontend envía un dict con id_turno y fecha_hora
                    if isinstance(item, dict):
                        fecha_str = item.get("fecha_hora")
                        id_turno = item.get("id_turno")
                    else:
                        fecha_str = item
                        id_turno = None

                    if not fecha_str:
                        continue

                    try:
                        # Asegurarse de que es un string válido ISO o con espacio
                        if isinstance(fecha_str, str):
                            fecha_atencion = datetime.fromisoformat(fecha_str)
                        else:
                            raise ValueError("Fecha inválida")

                        # Crear el registro de Monitoreo
                        Monitoreo.objects.create(
                            tratamiento=tratamiento,
                            fecha_atencion=fecha_atencion,
                            descripcion="Monitoreo programado desde segunda consulta",
                        )
                        if id_turno:
                            payload = {"id_paciente": tratamiento.paciente.id, "id_turno": id_turno}
                            try:
                                resp = requests.patch(
                                    SUPABASE_RESERVAR_URL,
                                    headers={
                                        "Authorization": f"Bearer {SUPABASE_KEY_RESERVAR}",
                                    },
                                    json=payload,
                                )
                                if resp.ok:
                                    logger.info(f"✅ Turno {id_turno} reservado correctamente")
                                    
                                    Turno.objects.create(
                                        Paciente=tratamiento.paciente,
                                        Medico=tratamiento.medico,
                                        fecha_hora=fecha_atencion,
                                        id_externo=id_turno,
                                        es_monitoreo=True,
                                    )
                                    
                                else:
                                    logger.warning(
                                        f"⚠️ No se pudo reservar turno {id_turno}. "
                                        f"Status {resp.status_code}: {resp.text}"
                                    )
                            except Exception as e:
                                logger.error(f"❌ Error al reservar turno {id_turno}: {e}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Fecha de monitoreo inválida: {fecha_str}. Error: {e}")

                # ---------- 6️⃣ Actualizar Resultados de Estudios ----------
                for est in estudios:
                    try:
                        resultado = ResultadoEstudio.objects.get(id=est["id"])
                        resultado.valor = est.get("valor")
                        resultado.save()
                    except ResultadoEstudio.DoesNotExist:
                        logger.warning(f"Estudio ID {est.get('id')} no encontrado")

                # ---------- 7️⃣ Generar Orden Médica de la Droga ----------
                try:
                    payload = {
                        "tipo_estudio": "orden_droga",
                        "droga": protocolo.get("droga"),
                        "tipo_medicacion": protocolo.get("tipo"),
                        "dosis_medicacion": protocolo.get("dosis"),
                        "duracion_medicacion": protocolo.get("duracion"),
                        "paciente": {
                            "nombre": f"{tratamiento.paciente.first_name} {tratamiento.paciente.last_name}",
                            "dni": getattr(tratamiento.paciente, "dni", None),
                        },
                        "medico": {
                            "nombre": f"{tratamiento.medico.first_name} {tratamiento.medico.last_name}",
                        },
                    }

                    # 🧾 Construir payload para multipart/form-data
                    files = {
                        "payload": (None, json.dumps(payload), "application/json"),
                    }

                    # 📎 Adjuntar la firma si existe
                    if getattr(tratamiento.medico, "firma_medico", None):
                        try:
                            with open(tratamiento.medico.firma_medico.path, "rb") as f:
                                firma_bytes = f.read()
                            files["firma_medico"] = ("firma.png", BytesIO(firma_bytes), "image/png")
                            logger.info("🖋️ Firma del médico adjuntada correctamente.")
                        except Exception as e:
                            logger.warning(f"⚠️ No se pudo leer la firma del médico: {e}")

                    # 🔧 Headers (sin Content-Type fijo, requests lo define automáticamente)
                    headers = {
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    }

                    # 📤 Enviar datos a la Edge Function de Supabase
                    logger.info("📤 Enviando datos a Edge Function de Supabase (con firma adjunta)...")
                    resp = requests.post(SUPABASE_EDGE_URL, headers=headers, files=files)

                    if resp.status_code == 200 and resp.headers.get("Content-Type") == "application/pdf":
                        pdf_bytes = resp.content
                        filename = f"orden_droga_tratamiento_{tratamiento.id}.pdf"

                        # 💾 Guardar el PDF en el modelo SegundaConsulta
                        segunda.orden_droga_pdf.save(filename, ContentFile(pdf_bytes))
                        segunda.save(update_fields=["orden_droga_pdf"])

                        logger.info(f"📄 Orden médica guardada y con firma: {segunda.orden_droga_pdf.url}")
                    else:
                        logger.error(f"❌ Error generando orden médica en Supabase: {resp.text}")

                except Exception as e:
                    logger.error(f"❌ Error generando orden médica en Supabase: {e}")
                    
                try:
                    # 📩 Email del paciente y nombre del médico
                    paciente_email = tratamiento.paciente.email
                    medico_nombre = f"{tratamiento.medico.first_name} {tratamiento.medico.last_name}"

                    if not paciente_email:
                        logger.warning("⚠️ Paciente sin email registrado, no se envía correo.")
                        raise Exception("Paciente sin email")

                    # 📄 URL ABSOLUTA al PDF guardado en el campo FileField
                    #    Esto evita hardcodear HOST o DOMAIN
                    #    Ejemplo: http://localhost:8000/media/segunda_consulta/orden_xxx.pdf
                    pdf_url = request.build_absolute_uri(segunda.orden_droga_pdf.url)

                    # 📨 Email HTML SEGURO (sin emojis ni caracteres que rompen la API)
                    html_body = (
                        f"<p>Hola {tratamiento.paciente.first_name},</p>"
                        f"<p>Tu médico <strong>{medico_nombre}</strong> ha generado una nueva orden médica de medicación.</p>"
                        f"<p>Puedes descargarla haciendo clic aquí:</p>"
                        f"<p><a href=\"{pdf_url}\" target=\"_blank\">Descargar orden médica (PDF)</a></p>"
                        f"<p>Saludos,<br>Clínica de Fertilidad</p>"
                    )

                    # 🌐 API de Avisos (NO SOPORTA ADJUNTOS)
                    url = "https://mvvuegssraetbyzeifov.supabase.co/functions/v1/send_email_v2"

                    payload = {
                        "group": 1,  # 🔥 tu grupo real: 8
                        "toEmails": [paciente_email],
                        "subject": "Orden medica de medicacion",
                        "htmlBody": html_body,
                    }

                    headers = {"Content-Type": "application/json"}

                    # 📤 Enviar mail por API
                    resp_mail = requests.post(url, json=payload, headers=headers)

                    if resp_mail.status_code == 200:
                        logger.info(f"📧 Orden médica enviada correctamente a {paciente_email}")
                    else:
                        logger.error(f"❌ Error API avisos: {resp_mail.status_code} - {resp_mail.text}")

                except Exception as e:
                    logger.error(f"❌ Error enviando correo con la API de avisos: {e}")



                # ---------- 8️⃣ Respuesta ----------
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
