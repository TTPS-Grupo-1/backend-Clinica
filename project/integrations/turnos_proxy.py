import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def turnos_proxy(request):
    id_medico = request.GET.get('id_medico', '1')
    token = request.headers.get('Authorization')
    if not token:
        # Token fijo si no se envía desde el frontend
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc"

    url = f"https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico?id_medico={id_medico}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=502)