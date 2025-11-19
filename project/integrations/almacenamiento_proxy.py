import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def almacenamiento_proxy(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        group_number = request.GET.get('group_number')
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        tank_type = request.GET.get('type')

        if not group_number:
            return JsonResponse({'error': 'group_number es requerido'}, status=400)

        base_url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/almacenamiento"
        params = {
            'group_number': 1,
            'page': page,
            'page_size': page_size,
        }
        if tank_type:
            params['type'] = tank_type

        headers = {"Content-Type": "application/json"}
        resp = requests.get(base_url, headers=headers, params=params, timeout=10)
        try:
            return JsonResponse(resp.json(), safe=False)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Respuesta no es JSON válido', 'raw': resp.text}, status=502)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)