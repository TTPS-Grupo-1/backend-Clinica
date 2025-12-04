import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

@csrf_exempt
def gametos_proxy(request):
    logger = logging.getLogger(__name__)
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        # Obtener datos del body
        data = json.loads(request.body) if request.body else {}
        logger.info(f"📨 Proxy recibió: {data}")

        gameto_type = data.get('type')
        phenotype = data.get('phenotype', {})

        logger.info(f"🔍 Tipo: {gameto_type}, Fenotipo: {phenotype}")
        
        if not gameto_type:
            return JsonResponse({'error': 'type es requerido'}, status=400)

        # URL de la API de Supabase para gametos
        base_url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/gametos-compatibilidad"
        
        # Preparar payload
        payload = {
            'group_number': 1,
            'type': gameto_type,
            'phenotype': phenotype
        }

        logger.info(f"🚀 Enviando a Supabase: {payload}")
        headers = {"Content-Type": "application/json"}
        resp = requests.post(base_url, headers=headers, json=payload, timeout=10)
        logger.info(f"📡 Respuesta de Supabase - Status: {resp.status_code}")
        logger.info(f"📡 Respuesta de Supabase - Body: {resp.text[:500]}")  # Primeros 500 chars
        
        try:
            response_data = resp.json()
            logger.info(f"✅ JSON parseado correctamente: {response_data}")
            return JsonResponse(response_data, safe=False)
        except ValueError as e:
            logger.error(f"❌ Error parseando JSON: {e}")
            return JsonResponse({'success': False, 'error': 'Respuesta no es JSON válido', 'raw': resp.text}, status=502)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error decodificando body: {e}")
        return JsonResponse({'error': 'Body debe ser JSON válido'}, status=400)
    except Exception as e:
        logger.error(f"❌ Error general en proxy: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)