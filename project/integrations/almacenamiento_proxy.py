import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def almacenamiento_proxy(request):
    # Parámetros esperados
    group_number = request.GET.get('group_number')
    page = request.GET.get('page', '1')
    page_size = request.GET.get('page_size', '10')
    tank_type = request.GET.get('type')

    # Validación básica
    if not group_number:
        return JsonResponse({'error': 'group_number es requerido'}, status=400)

    # Construir la URL y el body
    base_url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/almacenamiento"
    params = {
        'group_number': group_number,
        'page': page,
        'page_size': page_size,
    }
    if tank_type:
        params['type'] = tank_type

    url = base_url

    headers = {
        "Content-Type": "application/json",
        # "apikey": "TU_ANON_KEY",  # si la API lo requiere
        # "Authorization": "Bearer TU_ANON_KEY",  # si la API lo requiere
    }

    # Realiza la petición GET al API de terceros
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    try:
        data = resp.json()
        return JsonResponse(data, safe=False)
    except ValueError:
        # Si la respuesta no es JSON válido, devolver el texto y status
        return JsonResponse({
            'success': False,
            'error': 'Respuesta no es JSON válido',
            'raw': resp.text
        }, status=502)