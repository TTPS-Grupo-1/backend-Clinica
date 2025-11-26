import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DeudaPacienteView(APIView):
    SUPABASE_URL = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/deuda-paciente"

    def post(self, request):
        id_paciente = request.data.get("id_paciente")
        numero_grupo = request.data.get("numero_grupo")

        # 🔍 Validaciones iniciales
        if not id_paciente or not numero_grupo:
            return Response(
                {"error": "Los parámetros id_paciente y numero_grupo son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 👉 Forward al Supabase Function (POST)
            resp = requests.post(
                self.SUPABASE_URL,
                json={"id_paciente": id_paciente, "numero_grupo": numero_grupo},
                timeout=10,
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Error de conexión con Supabase: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # 🔍 Si Supabase devuelve error
        if resp.status_code >= 400:
            return Response(
                {
                    "error": "Error desde Supabase.",
                    "detalle": resp.text
                },
                status=resp.status_code,
            )

        # 🔥 Éxito
        return Response(resp.json(), status=status.HTTP_200_OK)
