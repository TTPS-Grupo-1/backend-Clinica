from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from ..serializers import PrimeraConsultaSerializer
from ..models import PrimeraConsulta
from .. import models as pc_models
from .. import serializers as pc_serializers
from AntecedentesGinecologicos.models import AntecedentesGinecologicos
import logging

logger = logging.getLogger(__name__)


class CreatePrimeraConsultaMixin:
    """
    Mixin para manejar la creación de PrimeraConsulta.
    Sigue la misma estructura y formato de respuesta que CreatePacienteMixin.
    """

    def create(self, request, *args, **kwargs):
        payload = request.data

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
        form = payload.get('form', {}) if isinstance(payload, dict) else {}
        paciente_id = payload.get('paciente') or form.get('paciente_id') or form.get('paciente')
        medico_id = payload.get('medico') or form.get('medico_id') or form.get('medico')

        if paciente_id:
            consulta_data['paciente'] = paciente_id
        else:
            # si no viene paciente, intentar usar user asociado (opcional)
            user = getattr(request, 'user', None)
            paciente_fk = None
            try:
                paciente_fk = getattr(user, 'paciente', None)
            except Exception:
                paciente_fk = None
            if paciente_fk:
                consulta_data['paciente'] = paciente_fk.id

        if medico_id:
            consulta_data['medico'] = medico_id

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
        try:
            antig = form.get('antecedentes_ginecologicos', {}) or {'antecedentes_ginecologicos_mujer1'}
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
            antig2 = form.get('antecedentes_ginecologicos_mujer2', {}) or {}
            datos2 = antig2.get('datos1', {}) or {}

            antecedentes_payload2 = {
                'menarca_2': safe_int(datos2.get('menarca')),
                'ciclo_menstrual_2': safe_int(datos2.get('ciclos')),
                'regularidad_2': datos2.get('regularidad') or None,
                'duracion_menstrual_dias_2': safe_int(datos2.get('duracion')),
                'caracteristicas_sangrado_2': datos2.get('sangrado') or None,
                'g_2': safe_int(datos2.get('g')),
                'p_2': safe_int(datos2.get('p')),
                'ab_2': safe_int(datos2.get('ab')),
                'st_2': safe_int(datos2.get('st')),
            }
        except Exception:
            antecedentes_payload = None
            antecedentes_payload2 = None
        try:
            antp = form.get('personales') or {'personales_mujer1'} or {'personales_mujer'}
            antecedentes_personales_payload = {}

        except Exception:
            antecedentes_payload = None
            antecedentes_payload2 = None

        #except Exception:
            

        # Crear todo en una transacción para mantener consistencia
        try:
            with transaction.atomic():
                consulta = serializer.save()

                # Crear antecedentes vinculados si vienen datos
                if antecedentes_payload and any(v is not None for v in antecedentes_payload.values()):
                    # Asignar FK 'consulta' en AntecedentesGinecologicos
                    AntecedentesGinecologicos.objects.create(consulta=consulta, **antecedentes_payload)
                    
                if antecedentes_payload2 and any(v is not None for v in antecedentes_payload2.values()):
                    AntecedentesGinecologicos.objects.create(consulta=consulta, **antecedentes_payload2)

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
