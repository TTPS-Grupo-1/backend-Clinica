from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from ..serializers import PrimeraConsultaSerializer
from ..models import PrimeraConsulta
from .. import models as pc_models
from .. import serializers as pc_serializers
from AntecedentesGinecologicos.models import AntecedentesGinecologicos
from AntecedentesPersonales.models import AntecedentesPersonales
from Fenotipo.models import Fenotipo
from ResultadoEstudio.models import ResultadoEstudio
from Orden.models import Orden
from Tratamiento.models import Tratamiento
from Orden.orden_service import generar_orden_y_guardar
import logging
from Orden.orden_email_service import enviar_ordenes_por_email
from .generar_orden_pago import registrar_orden_pago
from CustomUser.models import CustomUser
import requests


logger = logging.getLogger(__name__)


class CreatePrimeraConsultaMixin:
    """
    Mixin para manejar la creación de PrimeraConsulta.
    Sigue la misma estructura y formato de respuesta que CreatePacienteMixin.
    """

    def create(self, request, *args, **kwargs):
        
        
        
        payload = request.data
        print("Payload recibido:", payload)
        # Helper to safely convert numeric-like strings to int or None
        def safe_int(v):
            try:
                if v is None or v == "":
                    return None
                return int(v)
            except (TypeError, ValueError):
                return None

        # Normalizar datos principales de PrimeraConsulta
        consulta_data = {}
        consulta_data['objetivo_consulta'] = payload.get('objetivo') or payload.get('objetivo_consulta')

        # Obtener paciente y medico (buscar en payload o en form)
       # Obtener paciente y médico (admite *_id o relaciones)
       

# 🔹 Extraer el objetivo y desanidar si corresponde
       # Obtener el form desde el payload
        form = payload.get('form', {}) if isinstance(payload, dict) else {}

        # 🔹 Extraer el objetivo y desanidar si corresponde
        objetivo = payload.get('objetivo')
        if objetivo and isinstance(form.get(objetivo), dict):
            form = form.get(objetivo)


        paciente_id = (
            payload.get('paciente_id')
            or payload.get('paciente')
            or form.get('paciente_id')
            or form.get('paciente')
        )

        medico_id = (
            payload.get('medico_id')
            or payload.get('medico')
            or form.get('medico_id')
            or form.get('medico')
        )
        
        print("paciente_id:", paciente_id)
        SUPABASE_DEUDA_PACIENTE = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/deuda-paciente"
        GRUPO = 1
        deuda_resp = requests.post(
                SUPABASE_DEUDA_PACIENTE,
                json={"id_paciente": paciente_id, "numero_grupo": GRUPO},
                timeout=10
            )
        deuda = deuda_resp.json().get("deuda_total")
        if deuda and deuda > 0:
            return Response(
                {
                    "success": False,
                    "message": "El paciente tiene una deuda pendiente. No se puede iniciar un nuevo tratamiento.",
                    "deuda": deuda
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        print("medico_id:", medico_id)


           

        # Preparar serializer solo para la consulta (sin antecedentes)
        # Mapear campos de 'form' adicionales al modelo PrimeraConsulta
        # Familiares
        consulta_data['antecedentes_familiares_1'] = (
            form.get('familiares_mujer') or form.get('familiares_mujer1') or form.get('familiares') or form.get('familiares_1') or None
        )
        consulta_data['antecedentes_familiares_2'] = (
            form.get('familiares_mujer2') or form.get('familiares_hombre') or form.get('familiares_2') or None
        )

        # Genitales
        consulta_data['antecedentes_genitales'] = (
            form.get('antecedentes_genitales') or (form.get('genitales_hombre') or {}).get('descripcion') or None
        )

        # Antecedentes quirúrgicos
        
        # --- Antecedentes quirúrgicos ---
        def normalize_dict(value):
            """Convierte cualquier cosa a dict seguro"""
            if isinstance(value, dict):
                return value
            elif isinstance(value, (list, set, tuple)):
                # Si es un conjunto o lista, devolverlo como {"items": [...]} para no romper
                return {"items": list(value)}
            elif isinstance(value, str):
                return {"descripcion": value}
            else:
                return {}

        aq_mujer_raw = (
            form.get('antecedentes_quirurgicos_mujer')
            or form.get('antecedentes_quirurgicos_mujer1')
            or form.get('antecedentes_quirurgicos_mujer2')
        )
        aq_hombre_raw = (
            form.get('antecedentes_quirurgicos_hombre')
            or form.get('antecedentes_quirurgicos_hombre1')
            or form.get('antecedentes_quirurgicos_mujer2')
        )

        aq_mujer = normalize_dict(aq_mujer_raw)
        aq_hombre = normalize_dict(aq_hombre_raw)

        consulta_data['antecedentes_quirurgicos_1'] = (
            aq_mujer.get('descripcion')
        )

        consulta_data['antecedentes_quirurgicos_2'] = (
            aq_hombre.get('descripcion')
        )

        # Examen físico
        consulta_data['examen_fisico_1'] = (
            form.get('examen_fisico_mujer') or form.get('examen_fisico_hombre') or form.get('examen_fisico') or form.get('examen_fisico_mujer1') or None
        )
        consulta_data['examen_fisico_2'] = form.get('examen_fisico_mujer2') or form.get('examen_fisico_hombre') or None
        antecedentes_clinicos_1 = form.get('clinicos') or form.get('clinicos_mujer1') or form.get('clinicos_mujer') or None
        antecedentes_clinicos_2 = form.get('clinicos_mujer2') or form.get('clinicos_hombre') or None
        print("Antecedentes clínicos 1:", antecedentes_clinicos_1)
        print("Antecedentes clínicos 2:", antecedentes_clinicos_2)
        consulta_data['antecedentes_clinicos_1'] = antecedentes_clinicos_1
        consulta_data['antecedentes_clinicos_2'] = antecedentes_clinicos_2
        print("Datos normalizados para PrimeraConsulta:", consulta_data)
        serializer = self.get_serializer(data=consulta_data)

        if not serializer.is_valid():
            logger.warning(f"Errores de validación primera consulta: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Hay errores en los campos ingresados.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extraer antecedentes ginecológicos desde payload.form
        antecedentes_payload = None
        antecedentes_payload2 = None

        try:
            # 🔹 Buscar antecedentes ginecológicos (mujer 1 o general)
            antig = (
                form.get('antecedentes_ginecologicos')
                or form.get('antecedentes_ginecologicos_mujer1')
                or {}
            )
            datos1 = antig.get('datos1', {}) or {}

            antecedentes_payload = {
                'menarca': safe_int(datos1.get('menarca')),
                'ciclo_menstrual': safe_int(datos1.get('ciclos')),
                'regularidad': datos1.get('regularidad') or None,
                'duracion_menstrual_dias': safe_int(datos1.get('duracion')),
                'caracteristicas_sangrado': datos1.get('sangrado') or None,
                'g': safe_int(datos1.get('g')),
                'p': safe_int(datos1.get('p')),
                'ab': safe_int(datos1.get('ab')),
                'st': safe_int(datos1.get('st')),
            }

            # 🔹 Buscar antecedentes ginecológicos (mujer 2)
            antig2 = form.get('antecedentes_ginecologicos_mujer2') or {}
            datos2 = antig2.get('datos1', {}) or {}

            antecedentes_payload2 = {
                'menarca': safe_int(datos2.get('menarca')),
                'ciclo_menstrual': safe_int(datos2.get('ciclos')),
                'regularidad': datos2.get('regularidad') or None,
                'duracion_menstrual_dias': safe_int(datos2.get('duracion')),
                'caracteristicas_sangrado': datos2.get('sangrado') or None,
                'g': safe_int(datos2.get('g')),
                'p': safe_int(datos2.get('p')),
                'ab': safe_int(datos2.get('ab')),
                'st': safe_int(datos2.get('st')),
            }

        except Exception as e:
            print("🔥 Error en bloque ginecológicos:", type(e).__name__, e)
            antecedentes_payload = None
            antecedentes_payload2 = None


        # 🔹 Antecedentes personales
        antp = (
            form.get('personales')
            or form.get('personales_mujer1')
            or form.get('personales_mujer')
            or {}
        )
        print("antp:", antp)

        antecedentes_personales_payload = {
            'fuma_pack_dias': antp.get('fuma'),
            'consume_alcohol': antp.get('alcohol'),
            'drogas_recreativas': antp.get('drogas'),
            'observaciones_habitos': antp.get('observaciones'),
        }
        print("payload personales 1:", antecedentes_personales_payload)

        antp2 = (
            form.get('personales_mujer2')
            or form.get('personales_hombre')
            or {}
        )
        print("antp2:", antp2)

        antecedentes_personales_payload2 = {
            'fuma_pack_dias': antp2.get('fuma'),
            'consume_alcohol': antp2.get('alcohol'),
            'drogas_recreativas': antp2.get('drogas'),
            'observaciones_habitos': antp2.get('observaciones'),
        }
        print("payload personales 2:", antecedentes_personales_payload2)


        # 🔹 Fenotipo
        try:
            fenotipo_data = form.get('fenotipo', {}) or {}
            fenotipo_payload = {
                'color_ojos': fenotipo_data.get('ojos'),
                'color_pelo': fenotipo_data.get('peloColor'),
                'tipo_pelo': fenotipo_data.get('peloTipo'),
                'altura_cm': safe_int(fenotipo_data.get('altura')),
                'complexion_corporal': fenotipo_data.get('complexion'),
                'rasgos_etnicos': fenotipo_data.get('etnia'),
            }
            print("fenotipo:", fenotipo_payload)
            
            fenotipo_data2 = form.get('fenotipo2', {}) or {}
            fenotipo_payload2 = {
                'color_ojos': fenotipo_data2.get('ojos'),
                'color_pelo': fenotipo_data2.get('peloColor'),
                'tipo_pelo': fenotipo_data2.get('peloTipo'),
                'altura_cm': safe_int(fenotipo_data2.get('altura')),
                'complexion_corporal': fenotipo_data2.get('complexion'),
                'rasgos_etnicos': fenotipo_data2.get('etnia'),
            }
            print("fenotipo 2:", fenotipo_payload2)

        except Exception as e:
            print("🔥 Error en bloque fenotipo:", type(e).__name__, e)
            fenotipo_payload = None

        estudios_ginecologicos_1 = form.get('estudios_ginecologicos', {}).get('seleccionados') or form.get('estudios_ginecologicos_mujer1', {}).get('seleccionados') or None
        estudios_ginecologicos_2 = form.get('estudios_ginecologicos_mujer2', {}).get('seleccionados') or None

        # Inicializar todas las variables para evitar errores
        nombre_estudios_preq_1 = []
        nombre_estudios_preq_2 = []

        try:
            # --- Estudios prequirúrgicos ---
            e1 = form.get('estudios_prequirurgicos') or form.get('estudios_prequirurgicos_mujer1') \
                or form.get('estudios_prequirurgicos_mujer') or form.get('prequirurgicos') or {}
            e2 = form.get('estudios_prequirurgicos_mujer2') or form.get('estudios_prequirurgicos_hombre') or {}

            print("estudios prequirurgicos 1 raw:", e1)
            print("estudios prequirurgicos 2 raw:", e2)

            # 🔹 Si vienen anidados dentro de "valores", los extraemos
            if isinstance(e1, dict) and "valores" in e1:
                e1 = e1["valores"]
            if isinstance(e2, dict) and "valores" in e2:
                e2 = e2["valores"]

            nombre_estudios_preq_1 = [nombre for nombre, valor in e1.items() if valor]
            nombre_estudios_preq_2 = [nombre for nombre, valor in e2.items() if valor]

            print("🧾 estudios prequirurgicos 1:", nombre_estudios_preq_1)
            print("🧾 estudios prequirurgicos 2:", nombre_estudios_preq_2)

        except Exception as e:
            print("⚠️ Error procesando estudios prequirúrgicos:", str(e))


        estudios_semen = form.get('estudios_semen', {}).get('estudiosSeleccionados') or None
        
        print ("estudios semen:", estudios_semen)
        
        estudios_hormonales_1 = form.get('hormonales', {}).get('seleccionados') or form.get('hormonales_mujer1', {}).get('seleccionados') or None
        estudios_hormonales_2 = form.get('hormonales_mujer2', {}).get('seleccionados') or form.get('hormonales_hombre', {}).get('seleccionados') or None
        
        
        
        # Crear todo en una transacción para mantener consistencia
        try:
            with transaction.atomic():
                consulta = serializer.save()
                paciente = CustomUser.objects.get(id=paciente_id)
                medico = CustomUser.objects.get(id=medico_id)
               
                # Crear el tratamiento vinculado a esta primera consulta
                tratamiento = Tratamiento.objects.create(
                    paciente=paciente,
                    medico=medico,
                    primera_consulta=consulta,
                    objetivo=consulta.objetivo_consulta or "Tratamiento inicial",
                )

                # Crear antecedentes vinculados si vienen datos
                if antecedentes_payload and any(v is not None for v in antecedentes_payload.values()):
                    # Asignar FK 'consulta' en AntecedentesGinecologicos
                    AntecedentesGinecologicos.objects.create(consulta=consulta, **antecedentes_payload)
                    
                if antecedentes_payload2 and any(v is not None for v in antecedentes_payload2.values()):
                    AntecedentesGinecologicos.objects.create(consulta=consulta, **antecedentes_payload2)
                if antecedentes_personales_payload and any(v not in [None, ""] for v in antecedentes_personales_payload.values()):
                    logger.info(f"Creando AntecedentesPersonales1: {antecedentes_personales_payload}")

                    AntecedentesPersonales.objects.create(consulta=consulta, **antecedentes_personales_payload)
                if antecedentes_personales_payload2 and any(v not in [None, ""] for v in antecedentes_personales_payload2.values()):
                    logger.info(f"Creando AntecedentesPersonales2: {antecedentes_personales_payload2}")
                    AntecedentesPersonales.objects.create(consulta=consulta, **antecedentes_personales_payload2)
                    
                if fenotipo_payload and any(v not in [None, ""] for v in fenotipo_payload.values()):
                    Fenotipo.objects.create(consulta=consulta, **fenotipo_payload, persona="PACIENTE")

                if fenotipo_payload2 and any(v not in [None, ""] for v in fenotipo_payload2.values()):
                    Fenotipo.objects.create(consulta=consulta, **fenotipo_payload2, persona="ACOMPAÑANTE")

                if estudios_ginecologicos_1:
                    for estudio_nombre in estudios_ginecologicos_1:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="GINECOLOGICO",
                            nombre_estudio=estudio_nombre,
                            persona= "PACIENTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_ginecologicos",
                                            determinaciones=estudios_ginecologicos_1,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="no")
                if estudios_ginecologicos_2:
                    for estudio_nombre in estudios_ginecologicos_2:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="GINECOLOGICO",
                            nombre_estudio=estudio_nombre,
                            persona= "ACOMPAÑANTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_ginecologicos",
                                            determinaciones=estudios_ginecologicos_2,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="si")
                if nombre_estudios_preq_1:
                    for estudio_nombre in nombre_estudios_preq_1:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="PREQUIRURGICO",
                            nombre_estudio=estudio_nombre,
                            persona= "PACIENTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_prequirurgicos",
                                            determinaciones=nombre_estudios_preq_1,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="no")
                if nombre_estudios_preq_2:
                    for estudio_nombre in nombre_estudios_preq_2:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="PREQUIRURGICO",
                            nombre_estudio=estudio_nombre,
                            persona= "ACOMPAÑANTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_prequirurgicos",
                                            determinaciones=nombre_estudios_preq_2,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="si")
                if estudios_semen:
                    for estudio_nombre in estudios_semen:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="SEMINAL",
                            nombre_estudio=estudio_nombre,
                            persona= "ACOMPAÑANTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_semen",
                                            determinaciones=estudios_semen,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="si")
                if estudios_hormonales_1:
                    for estudio_nombre in estudios_hormonales_1:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="HORMONAL",
                            nombre_estudio=estudio_nombre,
                            persona= "PACIENTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_hormonales",
                                            determinaciones=estudios_hormonales_1,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="no")
                if estudios_hormonales_2:
                    for estudio_nombre in estudios_hormonales_2:
                        ResultadoEstudio.objects.create(
                            consulta=consulta,
                            tipo_estudio="HORMONAL",
                            nombre_estudio=estudio_nombre,
                            persona= "ACOMPAÑANTE"
                        )
                    generar_orden_y_guardar(consulta=consulta,
                                            tipo_estudio="estudios_hormonales",
                                            determinaciones=estudios_hormonales_2,
                                            medico=medico,
                                            paciente=paciente,
                                            acompañante="si")
                # Enviar órdenes por email al paciente
                enviar_ordenes_por_email(consulta)

                # Registrar orden de pago (usando la instancia de paciente)
                print("Paciente obra social:", paciente.obra_social)
                print("Datos de la orden de pago:")
                print("Grupo:", 1)
                print("ID Paciente:", paciente.id)
                print("Monto:", 1000000)
                pago = registrar_orden_pago(paciente.id, paciente.obra_social, 1, 1000000)
                id_pago = pago.get("pago", {}).get("id")
                tratamiento.id_pago = id_pago
                tratamiento.save()



            logger.info(f"Primera consulta creada: {consulta.id}")
            return Response(
                {
                    "success": True,
                    "message": "Primera consulta registrada correctamente.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            logger.error(f"Error de integridad: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Error de integridad en la base de datos.",
                    "errors": {"non_field_errors": ["Error de integridad en la base de datos."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception("Error inesperado al crear primera consulta.")
            return Response(
                {
                    "success": False,
                    "message": "Ocurrió un problema técnico al registrar la primera consulta. Por favor, intente nuevamente en unos momentos.",
                    "errors": {"server": [str(e)]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
