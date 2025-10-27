import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def almacenamiento_reserva_proxy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        group_number = data.get('group_number')
        tank_type = data.get('type')
        rack_count = data.get('rack_count')

        if not group_number or not tank_type or not rack_count:
            return JsonResponse({'error': 'Faltan parámetros requeridos'}, status=400)

        base_url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/tanques"
        payload = {
            'group_number': group_number,
            'type': tank_type,
            'rack_count': rack_count,
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(base_url, headers=headers, json=payload, timeout=10)
        try:
            return JsonResponse(resp.json(), safe=False, status=resp.status_code)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Respuesta no es JSON válido', 'raw': resp.text}, status=502)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)