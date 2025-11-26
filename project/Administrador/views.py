import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from CustomUser.models import CustomUser
from Tratamiento.models import Tratamiento


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
                "saldo_pendiente": deuda - cobrado if (deuda - cobrado) > 0 else 0
            })

        return Response(resultados, status=status.HTTP_200_OK)




# ==============================================
#  🔴 2) FINANZAS DE PACIENTES
# ==============================================
class PacientesFinanzasView(APIView):

    def get(self, request):

        # -----------------------------
        # 1) Obtener obras sociales
        # -----------------------------
        try:
            obras_resp = requests.get(SUPABASE_OBRAS, timeout=10)
            obras_data = obras_resp.json().get("data", [])
        except:
            obras_data = []

        # Crear diccionario: id → obra social
        obras_dict = {obra["id"]: obra for obra in obras_data}

        # -----------------------------
        # 2) Obtener pacientes con obra social asignada
        # -----------------------------
        pacientes = CustomUser.objects.filter(
            rol="PACIENTE"
        ).exclude(
            obra_social__isnull=True
        )

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

            # Excluir si no hay movimientos
            if deuda == 0 and cobrado == 0:
                continue

            # Obtener sigla y nombre de la obra social
            obra_social_info = obras_dict.get(obra_social_id, {})
            obra_sigla = obra_social_info.get("sigla", "N/D")
            obra_nombre = obra_social_info.get("nombre", "N/D")

            resultados.append({
                "id": id_paciente,
                "nombre": nombre,
                "obra_social_id": obra_social_id,
                "obra_social_sigla": obra_sigla,
                "obra_social_nombre": obra_nombre,
                "total_deuda": deuda,
                "total_cobrado": cobrado,
                "saldo_pendiente": deuda - cobrado if (deuda - cobrado) > 0 else 0
            })

        return Response(resultados, status=status.HTTP_200_OK)
    
class CobrarObraSocialView(APIView):
    SUPABASE_REGISTRAR_PAGO = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/registrar-pago-obra-social"
    GRUPO = 1  # o el número que uses

    def post(self, request):

        id_obra_social = request.data.get("id_obra_social")
        print("Iniciando proceso de cobro para obra social ID:", id_obra_social)

        if not id_obra_social:
            return Response(
                {"error": "El parámetro id_obra_social es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Pacientes con esa obra social
        pacientes = CustomUser.objects.filter(
            obra_social=id_obra_social,
            rol="PACIENTE",
            eliminado=False
        )
        print(f"Se encontraron {pacientes.count()} pacientes con obra social ID {id_obra_social}.")

        # 2) Tratamientos con id_pago
        tratamientos = Tratamiento.objects.filter(
            paciente__in=pacientes,
            id_pago__isnull=False
        )
        if not tratamientos.exists():
            return Response(
                {"message": "No hay pagos pendientes para esta obra social."},
                status=status.HTTP_200_OK
        )
        print(f"Se encontraron {tratamientos.count()} tratamientos con pagos pendientes.")
        resultados = []

            # 3) Llamar al endpoint Supabase por cada pago
        for t in tratamientos:
            try:
                resp = requests.post(
                    self.SUPABASE_REGISTRAR_PAGO,
                    json={
                        "id_grupo": self.GRUPO,
                        "id_pago": t.id_pago,
                        "obra_social_pagada": True,
                        "paciente_pagado": False
                    },
                    timeout=10
                )
                data = resp.json()
                print(data)

                if resp.status_code == 200:
                    resultados.append({
                        "tratamiento_id": t.id,
                        "id_pago": t.id_pago,
                        "respuesta": data
                    })
                else:
                    print(data)
                    print("Error al registrar pago en Supabase")
                    resultados.append({
                        "tratamiento_id": t.id,
                        "id_pago": t.id_pago,
                        "error": data
                    })
            except Exception as e:
                resultados.append({
                    "tratamiento_id": t.id,
                    "id_pago": t.id_pago,
                    "error": str(e)
                })
        return Response({
            "obra_social": id_obra_social,
            "total_pagos_procesados": len(resultados),
            "detalles": resultados
        }, status=status.HTTP_200_OK)



