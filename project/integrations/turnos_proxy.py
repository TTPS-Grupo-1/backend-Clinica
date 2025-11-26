# import requests
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def turnos_proxy(request):
#     id_medico = request.GET.get('id_medico', '1')
#     token = request.headers.get('Authorization')
#     if not token:
#         # Token fijo si no se envía desde el frontend
#         token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc"

#     url = f"https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico?id_medico={id_medico}"
#     headers = {
#         "Authorization": token,
#         "Content-Type": "application/json",
#     }
#     try:
#         resp = requests.get(url, headers=headers, timeout=10)
#         data = resp.json()
#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)}, status=502)

from datetime import datetime
from django.utils import timezone
from venv import logger
import requests
import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Turnos.models import Turno
from CustomUser.models import CustomUser
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# URL base para los endpoints de Supabase
API_BASE_URL = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1"
# Token de ejemplo fijo (usado para desarrollo/proxy)
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc"

# ----------------------------------------------------------------------
# 1. PROXY para GET (Consultar turnos de un médico)
# ----------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_get(request):
    """Proxy para GET /get_turnos_medico"""
    if request.method != 'GET':
        return JsonResponse({"success": False, "error": "Método no permitido. Use GET."}, status=405)

    id_medico = request.GET.get('id_medico')
    token = request.headers.get('Authorization', AUTH_TOKEN)

    url = f"{API_BASE_URL}/get_turnos_medico?id_medico={id_medico}"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return JsonResponse(resp.json(), status=resp.status_code)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=502)

# ----------------------------------------------------------------------
# 2. PROXY para POST (Crear grilla de turnos)
# ----------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_post(request):
    """Proxy para POST /post_turnos"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método no permitido. Use POST."}, status=405)

    token = request.headers.get('Authorization', AUTH_TOKEN)

    try:
        body_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Cuerpo de petición JSON inválido."}, status=400)
        
    url = f"{API_BASE_URL}/post_turnos"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    try:
        # Usamos json=body_data para que requests lo serialice correctamente
        resp = requests.post(url, headers=headers, json=body_data, timeout=10)
        
        # Devolver la respuesta de la API externa
        return JsonResponse(resp.json(), status=resp.status_code)
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "error": f"Error de conexión con la API externa: {str(e)}"}, status=502)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Error interno del proxy: {str(e)}"}, status=500)

# -------------------------------------------------------------------------------
# 3. PROXY para GET (Consulta turnos de un médico para una fecha específica )
# -------------------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_get_medico_fecha(request):

    if request.method != 'GET':
        return JsonResponse({"success": False, "error": "Método no permitido. Use GET."}, status=405)

    # Obtenemos los parámetros id_medico y fecha
    id_medico = request.GET.get('id_medico')
    fecha = request.GET.get('fecha')

    if not id_medico or not fecha:
        return JsonResponse({
            "success": False, 
            "error": "Faltan parámetros requeridos: id_medico y fecha (YYYY-MM-DD)."
        }, status=400)

    token = request.headers.get('Authorization', AUTH_TOKEN)
    
    # Construir la URL para get_medico_fecha
    url = f"{API_BASE_URL}/get_medico_fecha?id_medico={id_medico}&fecha={fecha}"
    
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return JsonResponse(resp.json(), status=resp.status_code, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "error": f"Error de conexión con la API externa: {str(e)}"}, status=502)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Error interno del proxy: {str(e)}"}, status=500)

# -------------------------------------------------------------------------------------------
# 4. PROXY para PATCH (Guardar el turno para el paciente) - Ademas lo guarda en la BD local
# -------------------------------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_reservar(request):
    if request.method != 'PATCH':
        return JsonResponse({"success": False, "error": "Método no permitido. Use PATCH."}, status=405)

    token = request.headers.get('Authorization', AUTH_TOKEN)
    
    try:
        body_data = json.loads(request.body)
        id_paciente = body_data.get('id_paciente')
        id_turno = body_data.get('id_turno')
        
        if not id_paciente or not id_turno:
            return JsonResponse({"success": False, "error": "Faltan id_paciente o id_turno."}, status=400)

        # 1. EJECUTAR PATCH EN LA API EXTERNA
        url_externa = f"{API_BASE_URL}/reservar_turno"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        
        resp = requests.patch(url_externa, headers=headers, json=body_data, timeout=10)
        resp_data = resp.json()

        # 2. VERIFICAR RESPUESTA EXITOSA (200 OK)
        if resp.status_code == 200 and resp_data.get('turno'):
            
            # --- LÓGICA DE ALMACENAMIENTO LOCAL EN DJANGO ---
            turno_externo = resp_data['turno']
            
            medico_pk_value = turno_externo['id_medico'] 
            paciente_id_value = turno_externo['id_paciente']
            fecha_hora_str = turno_externo['fecha_hora']
            id_turno_externo = turno_externo['id']
            
            try:
                with transaction.atomic():
                    # 2.1. Buscar instancias de CustomUser por ID y Rol
                    medico_instance = CustomUser.objects.get(id=medico_pk_value, rol='MEDICO') 
                    paciente_instance = CustomUser.objects.get(id=paciente_id_value, rol='PACIENTE')

                    # 2.2. Convertir fecha_hora a objeto datetime CONSCIENTE DE LA ZONA HORARIA
                    # Usamos strptime para compatibilidad con versiones antiguas de Python
                    FECHA_HORA_FORMATO = '%Y-%m-%dT%H:%M:%S%z' 
                    fecha_hora_con_offset = fecha_hora_str.replace('Z', '+00:00')
                    fecha_hora_dt = datetime.strptime(fecha_hora_con_offset, FECHA_HORA_FORMATO)
                    
                    # 2.3. Guardar el Turno en tu base de datos local
                    Turno.objects.create(
                        Paciente=paciente_instance, 
                        Medico=medico_instance,
                        fecha_hora=fecha_hora_dt,
                        id_externo=id_turno_externo,
                        # No incluimos 'estado' ni 'id'/'created_at' porque son automáticos
                    )
                
                # Devolver respuesta exitosa DE LA API EXTERNA
                return JsonResponse(resp_data, status=200) 
                
            except (CustomUser.DoesNotExist, ValueError) as e:
                # Captura si el usuario no existe o si el formato de fecha falla
                error_msg = f"Error de réplica local: Usuario no encontrado o formato de fecha inválido. Detalle: {str(e)}"
                logger.error(error_msg)
                return JsonResponse({"success": False, "error": error_msg}, status=500)
            
            except Exception as e:
                # Captura cualquier otro error de guardado (ej: integridad DB)
                error_msg = f"Error crítico al guardar turno localmente: {str(e)}"
                logger.info.error(error_msg)
                return JsonResponse({"success": False, "error": error_msg}, status=500)


        # 3. DEVOLVER ERRORES DE LA API EXTERNA (409, 400, etc.)
        return JsonResponse(resp_data, status=resp.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "error": f"Error de conexión con la API externa: {str(e)}"}, status=502)
    except Exception as e:
        # Error al parsear el JSON de entrada o error interno del proxy
        return JsonResponse({"success": False, "error": f"Error interno del servidor: {str(e)}"}, status=500)
   
# -------------------------------------------------------------------------------------------
# 5. Proxy para GET /get_turnos_paciente (Lista todos los turnos asignados a un paciente).
# -------------------------------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_get_turnos_paciente(request):

    if request.method != 'GET':
        return JsonResponse({"success": False, "error": "Método no permitido. Use GET."}, status=405)

    id_paciente = request.GET.get('id_paciente')

    if not id_paciente:
        return JsonResponse({
            "success": False,
            "error": "Falta el parámetro requerido: id_paciente."
        }, status=400)

    token = request.headers.get('Authorization', AUTH_TOKEN)
    
    url = f"{API_BASE_URL}/get_turnos_paciente?id_paciente={id_paciente}"
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)

        api_data = resp.json().get("data", [])

        # --- Mezclar con DB local ---
        from Turnos.models import Turno

        enriched_data = []
        for t in api_data:
            turno_local = Turno.objects.filter(id_externo=t["id"]).first()

            # Si existe en tu base, reemplazamos es_monitoreo
            if turno_local:
                t["es_monitoreo"] = bool(turno_local.es_monitoreo)
            else:
                t["es_monitoreo"] = False  # o lo que quieras por default

            enriched_data.append(t)

        return JsonResponse({"success": True, "data": enriched_data}, status=200)

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Error interno del proxy: {str(e)}"},
            status=500
        )

# ---------------------------------------------------------------------------------------------------
# 6. Proxy para PATCH /cancelar_turno (Libera el turno en la API y marca el turno cancelado local.).
# ---------------------------------------------------------------------------------------------------
@csrf_exempt
def turnos_proxy_cancelar(request):

    if request.method != 'PATCH':
        return JsonResponse({"success": False, "error": "Método no permitido. Use PATCH."}, status=405)

    token = request.headers.get('Authorization', AUTH_TOKEN)
    
    try:

        id_turno_ext = request.GET.get('id_turno')

        logger.info(f"ID API EXTERNO {id_turno_ext}")
  
        if not id_turno_ext:
            return JsonResponse({"success": False, "error": "Falta el parámetro id_turno en la URL."}, status=400)

        # --- LÓGICA DE BÚSQUEDA DEL ID EXTERNO Y ACTUALIZACIÓN LOCAL ---
        try:
            with transaction.atomic():
                
                # 2. Obtener el ID externo para la API
                turno_local = Turno.objects.get(id_externo=id_turno_ext)
                logger.info(f"ID LOCAL {turno_local}")
                # 3. EJECUTAR PATCH EN LA API EXTERNA
                # El endpoint de cancelación usa Query Params: /cancelar_turno?id_turno={id_externo}
                url_externa = f"{API_BASE_URL}/cancelar_turno?id_turno={id_turno_ext}"
                headers = {"Authorization": token, "Content-Type": "application/json"}
                
                resp = requests.patch(url_externa, headers=headers, timeout=10)
                resp_data = resp.json()

                # 4. VERIFICAR RESPUESTA EXITOSA (200 OK)
                if resp.status_code == 200:
                    
                    # 5. Marcar como cancelado en la BD local de Django
                    turno_local.cancelado = True 
                    turno_local.save()
                    
                    return JsonResponse(resp_data, status=200)

                # 6. Si la API externa falla, devolver el error de Supabase/API
                return JsonResponse(resp_data, status=resp.status_code)

        except Turno.DoesNotExist:
            return JsonResponse({"success": False, "error": f"El turno local con ID {id_turno_ext} no fue encontrado."}, status=404)
        
        except Exception as e:
            # Captura errores de conexión, DB local, etc.
            return JsonResponse({"success": False, "error": f"Error interno al cancelar: {str(e)}"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Cuerpo de petición JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Error interno del proxy: {str(e)}"}, status=500)