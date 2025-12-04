import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def gametos_donacion_proxy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        import json
        payload = json.loads(request.body)
        logger.info(f"📨 DONACIÓN recibida: {payload}")
        
        url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/gametos-donacion"
        headers = {
            "Content-Type": "application/json",
        }
        
        logger.info(f"🚀 Enviando donación a Supabase: {payload}")
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f"📡 Respuesta de Supabase - Status: {resp.status_code}")
        logger.info(f"📡 Respuesta de Supabase - Body: {resp.text[:500]}")
        
        try:
            data = resp.json()
            logger.info(f"✅ JSON parseado: {data}")
            
            # Verificar si la donación fue exitosa
            if data.get('success'):
                logger.info(f"✅✅✅ DONACIÓN EXITOSA - Grupo: {payload.get('group_number')}, Tipo: {payload.get('type')}")
            else:
                logger.warning(f"⚠️ DONACIÓN FALLÓ: {data.get('error')}")
            
            return JsonResponse(data, safe=False, status=resp.status_code)
        except ValueError as e:
            logger.error(f"❌ Error parseando respuesta: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Respuesta no es JSON válido',
                'raw': resp.text
            }, status=502)
    except Exception as e:
        logger.error(f"❌ Error en donación: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
