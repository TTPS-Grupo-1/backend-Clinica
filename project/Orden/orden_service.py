import requests
import json
import re
import unicodedata
from io import BytesIO
from supabase import create_client
from django.conf import settings
from .models import Orden


# ⚙️ Configuración Supabase (valores fijos por ahora)
SUPABASE_URL = "https://srlgceodssgoifgosyoh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybGdjZW9kc3Nnb2lmZ29zeW9oIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ0NTU3NiwiZXhwIjoyMDc2MDIxNTc2fQ.4KDD7JytM2J8jMxl6WmYyTArThY4Dd8s6ACJZdYMJMY"
SUPABASE_FUNCTION_URL = f"{SUPABASE_URL}/functions/v1/generar_orden_medica"
BUCKET = "ordenes"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def clean_filename(text: str) -> str:
    """Convierte texto a un nombre de archivo seguro (sin tildes, ñ, ni símbolos)."""
    if not text:
        return "archivo"
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", text.lower()).strip("_")
    return text


def generar_orden_y_guardar(consulta, tipo_estudio, determinaciones, medico, paciente, acompañante):
    """
    Genera una orden médica (PDF) usando una Edge Function de Supabase,
    la sube a Supabase Storage y la guarda en la base local.
    """
    print(f"📝 Generando orden para {tipo_estudio}...")
    # 1️⃣ Preparar payload para la función edge
    payload = {
        "tipo_estudio": tipo_estudio,
        "medico": {
            "nombre": f"{medico.first_name} {medico.last_name}",
        },
        "paciente": {
            "nombre": f"{paciente.first_name} {paciente.last_name}",
            "dni": getattr(paciente, "dni", None),
        },
        "determinaciones": [{"nombre": d} for d in determinaciones],
    }

    # 2️⃣ Preparar firma (si existe)
    files = {
        "payload": (None, json.dumps(payload), "application/json"),
    }

    firma_bytes = None
    if getattr(medico, "firma_medico", None):
        try:
            with open(medico.firma_medico.path, "rb") as f:
                firma_bytes = f.read()
            files["firma_medico"] = ("firma.png", BytesIO(firma_bytes), "image/png")
        except Exception as e:
            print("⚠️ No se pudo leer la firma:", e)

    headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}

    # 3️⃣ Llamar a la Edge Function
    res = requests.post(SUPABASE_FUNCTION_URL, headers=headers, files=files)
    if res.status_code != 200:
        print(f"⚠️ Error generando PDF ({res.status_code}): {res.text}")
        return None

    pdf_bytes = res.content

    # 4️⃣ Subir PDF al bucket
    bucket = supabase.storage.from_(BUCKET)
    tipo_estudio_clean = clean_filename(tipo_estudio)
    acomp_clean = clean_filename(str(acompañante))
    file_name = f"acompanante_{acomp_clean}_paciente_{paciente.id}_orden_{consulta.id}_{tipo_estudio_clean}.pdf"

    bucket.upload(
        path=file_name,
        file=pdf_bytes,
        file_options={"content_type": "application/pdf", "x-upsert": "true"},
    )

    pdf_url = bucket.get_public_url(file_name)

    # 5️⃣ Guardar la orden en la BD
    orden = Orden.objects.create(
        primera_consulta=consulta,
        tipo_estudio=tipo_estudio,
        pdf_url=pdf_url,
    )

    print(f"✅ Orden creada correctamente ({tipo_estudio}): {pdf_url}")
    return orden
