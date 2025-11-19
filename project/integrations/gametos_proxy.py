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
        

        gameto_type = data.get('type')
        phenotype = data.get('phenotype', {})


        
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

        headers = {"Content-Type": "application/json"}
        resp = requests.post(base_url, headers=headers, json=payload, timeout=10)
        logger.info("Solicitud enviada a la API de gametos.", resp)
        try:
            return JsonResponse(resp.json(), safe=False)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Respuesta no es JSON válido', 'raw': resp.text}, status=502)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Body debe ser JSON válido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)