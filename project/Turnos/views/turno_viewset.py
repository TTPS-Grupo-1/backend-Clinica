from rest_framework import viewsets
from rest_framework.decorators import action
from Turnos.models import Turno
from Turnos.serializers import TurnoSerializer
from Turnos.views.create_turno_view import CreateTurnoMixin
import requests
from django.http import JsonResponse
class TurnoViewSet(CreateTurnoMixin, viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer  

    @action(detail=False, methods=["get"], url_path="medico/(?P<id_medico>[^/.]+)")
    def get_turnos_medico_proxy(self, request, id_medico: int):
        print(f"📩 Consultando turnos para el médico con ID: {id_medico}")
        SUPABASE_EDGE_URL = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico"
        SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc" 
        try:
            url = f"{SUPABASE_EDGE_URL}?id_medico={id_medico}"
            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            }
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            print(f"✅ Respuesta recibida: {resp.json()}")
            return JsonResponse(resp.json(), safe=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar turnos: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
            return JsonResponse({"error": str(e)}, status=500)
