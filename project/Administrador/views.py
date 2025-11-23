import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from concurrent.futures import ThreadPoolExecutor, as_completed
from Tratamiento.models import Tratamiento
from CustomUser.models import CustomUser


SUPABASE_OBRAS = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/getObrasSociales"
SUPABASE_DEUDA_OBRA = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/deuda-obra-social"
SUPABASE_COBRADO_OBRA = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/total-cobrado-obra"

SUPABASE_DEUDA_PACIENTE = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/deuda-paciente"
SUPABASE_COBRADO_PACIENTE = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/total-cobrado-paciente"

GRUPO = 1   # <--- si siempre usás el mismo grupo


# ==============================================
#  🔵 1) FINANZAS OBRAS SOCIALES
# ==============================================
class ObrasSocialesFinanzasView(APIView):

    def get(self, request):

        # --------------------------------------------------
        # 1) Obtener IDs de obras sociales usadas en pacientes
        # --------------------------------------------------
        obras_ids_usadas = (
            CustomUser.objects
                .filter(rol="PACIENTE")
                .exclude(obra_social__isnull=True)
                .values_list("obra_social", flat=True)
                .distinct()
        )

        obras_ids_usadas = list(obras_ids_usadas)  # ej: [1, 3, 7]
        if not obras_ids_usadas:
            return Response([], status=status.HTTP_200_OK)

        # --------------------------------------------------
        # 2) Obtener todas las obras sociales desde Supabase
        # --------------------------------------------------
        obras_resp = requests.get(SUPABASE_OBRAS, timeout=10)
        todas_las_obras = obras_resp.json().get("data", [])

        # --------------------------------------------------
        # 3) Filtrar solo las obras que se usan en tu BD
        # --------------------------------------------------
        obras_filtradas = [
            obra for obra in todas_las_obras 
            if obra["id"] in obras_ids_usadas
        ]

        resultados = []

        # --------------------------------------------------
        # 4) De cada obra filtrada, obtener deuda + cobrado
        # --------------------------------------------------
        for obra in obras_filtradas:
            id_obra = obra["id"]
            nombre = obra["nombre"]

            # --- deuda ---
            deuda_resp = requests.post(
                SUPABASE_DEUDA_OBRA,
                json={"id_obra": id_obra, "numero_grupo": GRUPO},
                timeout=10
            )
            deuda = deuda_resp.json().get("deuda_total", 0)

            # --- cobrado ---
            cobrado_resp = requests.post(
                SUPABASE_COBRADO_OBRA,
                json={"id_obra": id_obra, "numero_grupo": GRUPO},
                timeout=10
            )
            cobrado = cobrado_resp.json().get("total_cobrado", 0)

            # excluir sin movimiento
            if deuda == 0 and cobrado == 0:
                continue

            resultados.append({
                "id": id_obra,
                "nombre": nombre,
                "total_deuda": deuda,
                "total_cobrado": cobrado,
                "saldo_pendiente": deuda - cobrado
            })

        return Response(resultados, status=status.HTTP_200_OK)




# ==============================================
#  🔴 2) FINANZAS DE PACIENTES
# ==============================================
class PacientesFinanzasView(APIView):

    def get(self, request):

        pacientes = CustomUser.objects.filter(rol="PACIENTE")

        resultados = []

        for paciente in pacientes:
            id_paciente = paciente.id
            obra_social_id = paciente.obra_social
            nombre = paciente.get_full_name()

            # --- deuda ---
            deuda_resp = requests.post(
                SUPABASE_DEUDA_PACIENTE,
                json={"id_paciente": id_paciente, "numero_grupo": GRUPO},
                timeout=10
            )
            deuda = deuda_resp.json().get("deuda_total", 0)

            # --- cobrado ---
            cobrado_resp = requests.post(
                SUPABASE_COBRADO_PACIENTE,
                json={"id_paciente": id_paciente, "numero_grupo": GRUPO},
                timeout=10
            )
            cobrado = cobrado_resp.json().get("total_cobrado", 0)

            resultados.append({
                "id": id_paciente,
                "nombre": nombre,
                "obra_social_id": obra_social_id,
                "total_deuda": deuda,
                "total_cobrado": cobrado,
                "saldo_pendiente": deuda - cobrado
            })

        return Response(resultados, status=status.HTTP_200_OK)
