import requests
import logging

# Crear instancia de logger para este módulo
logger = logging.getLogger(__name__)

def registrar_orden_pago(id_paciente: int, id_obra: int, grupo: int, monto: float):
    """
    Llama al endpoint de Supabase para registrar una orden de pago.
    """
    url = "https://ueozxvwsckonkqypfasa.supabase.co/functions/v1/registrar-orden-pago"
    payload = {
        "grupo": grupo,
        "id_paciente": id_paciente,
        "monto": monto,
        "id_obra": id_obra,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"💰 Orden de pago registrada en Supabase: {data}")
            return data
        else:
            logger.warning(
                f"⚠️ Supabase respondió con error {response.status_code}: {response.text}"
            )
            return {"success": False, "status": response.status_code, "error": response.text}

    except Exception as e:
        logger.error(f"❌ Error al registrar orden de pago en Supabase: {e}")
        return {"success": False, "error": str(e)}
