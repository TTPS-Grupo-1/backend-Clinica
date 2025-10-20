import requests
from supabase import create_client
from django.conf import settings
from models import Orden

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
SUPABASE_FUNCTION_URL = f"{SUPABASE_URL}/functions/v1/generar-orden"
BUCKET = "ordenes"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generar_orden_y_guardar(consulta, tipo_estudio, determinaciones, medico, paciente):
    """
    Llama a la Edge Function de Supabase para generar un PDF de orden médica,
    lo sube al bucket de Supabase Storage y guarda la URL en la base local.
    """
    # 1️⃣ Preparar payload
    payload = {
        "tipo_estudio": tipo_estudio,
        "medico": {"nombre": medico.nombre, "firma_url": medico.firma_url if hasattr(medico, "firma_url") else None},
        "paciente": {"nombre": paciente.nombre, "dni": paciente.dni},
        "determinaciones": [{"nombre": d} for d in determinaciones],
    }

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    # 2️⃣ Llamar a la función Edge
    res = requests.post(SUPABASE_FUNCTION_URL, headers=headers, json=payload)
    if res.status_code != 200:
        print("⚠️ Error generando PDF:", res.text)
        return None

    # 3️⃣ Obtener bytes PDF
    pdf_bytes = res.content

    # 4️⃣ Subir a Supabase Storage
    file_name = f"orden_{consulta.id}_{tipo_estudio.replace(' ', '_')}.pdf"
    upload_res = supabase.storage.from_(BUCKET).upload(f"{file_name}", pdf_bytes, {"upsert": True})
    pdf_url = supabase.storage.from_(BUCKET).get_public_url(file_name)

    # 5️⃣ Guardar en tu base local
    orden = Orden.objects.create(
        primera_consulta=consulta,
        tipo_estudio=tipo_estudio.lower().replace("estudios ", ""),
        nombre_estudio=", ".join(determinaciones),
        pdf_url=pdf_url
    )

    print("✅ Orden creada:", orden)
    return orden
