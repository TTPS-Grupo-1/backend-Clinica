import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def gametos_donacion_proxy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        import json
        print("Request body:", request.body)
        payload = json.loads(request.body)
        url = "https://omtalaimckjolwtkgqjw.supabase.co/functions/v1/gametos-donacion"
        headers = {
            "Content-Type": "application/json",
            # "apikey": "TU_ANON_KEY",  # si la API lo requiere
            # "Authorization": "Bearer TU_ANON_KEY",  # si la API lo requiere
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        try:
            data = resp.json()
            return JsonResponse(data, safe=False, status=resp.status_code)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Respuesta no es JSON válido',
                'raw': resp.text
            }, status=502)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
