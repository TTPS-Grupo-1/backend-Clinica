import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Tratamiento.models import Tratamiento


class RegistrarPagoView(APIView):
    SUPABASE_URL = (
        "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/registrar-pago-obra-social"
    )

    def post(self, request):
        id_grupo = request.data.get("id_grupo")
        id_paciente = request.data.get("id_paciente")
        obra_social_pagada = request.data.get("obra_social_pagada")
        paciente_pagado = request.data.get("paciente_pagado")

        # --------------------------------------------------------------------
        # Validaciones iniciales
        # --------------------------------------------------------------------
        if id_grupo is None or id_paciente is None:
            return Response(
                {"error": "Los parámetros id_grupo e id_paciente son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Uno de los dos booleanos debe ser True
        if obra_social_pagada is not True and paciente_pagado is not True:
            return Response(
                {"error": "Debe enviar obra_social_pagada=True o paciente_pagado=True."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------------
        # Obtener tratamiento más reciente
        # --------------------------------------------------------------------
        tratamiento = (
            Tratamiento.objects.filter(paciente_id=id_paciente)
            .order_by("-fecha_creacion")
            .first()
        )

        if not tratamiento:
            return Response(
                {"error": "No existe un tratamiento para este paciente."},
                status=status.HTTP_404_NOT_FOUND,
            )

        id_pago = tratamiento.id_pago

        if not id_pago:
            return Response(
                {"error": "El tratamiento no tiene un id_pago asociado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------------
        # Forward a SUPABASE
        # --------------------------------------------------------------------
        payload = {
            "id_grupo": id_grupo,
            "id_pago": id_pago,
            "obra_social_pagada": obra_social_pagada,
            "paciente_pagado": paciente_pagado,
        }

        try:
            resp = requests.post(self.SUPABASE_URL, json=payload, timeout=10)
        except requests.RequestException as e:
            return Response(
                {"error": f"Error de conexión con Supabase: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code >= 400:
            return Response(
                {
                    "error": "Supabase devolvió un error.",
                    "detalle": resp.text,
                    "payload_enviado": payload,
                },
                status=resp.status_code,
            )

        # --------------------------------------------------------------------
        # Respuesta final al frontend
        # --------------------------------------------------------------------
        return Response(
            {
                "success": True,
                "message": "Pago actualizado correctamente.",
                "supabase_response": resp.json(),
                "id_pago": id_pago,
                "id_paciente": id_paciente,
                "id_grupo": id_grupo,
            },
            status=status.HTTP_200_OK,
        )
