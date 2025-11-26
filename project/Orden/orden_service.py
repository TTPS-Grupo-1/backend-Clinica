import os
import json
import re
import unicodedata
import requests

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile

from Orden.models import Orden


# ⚙️ URL de tu Edge Function que genera el PDF
SUPABASE_FUNCTION_URL = "https://srlgceodssgoifgosyoh.supabase.co/functions/v1/generar_orden_medica"


def clean_filename(text: str) -> str:
    """Normaliza un texto para usarlo como nombre de archivo."""
    if not text:
        return "archivo"
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9_]+", "_", text.lower()).strip("_")


def generar_orden_y_guardar(consulta, tipo_estudio, determinaciones, medico, paciente, acompañante):
    """
    Genera una orden médica usando la Edge Function y la guarda localmente
    en MEDIA_ROOT/ordenes/.
    Retorna la instancia de Orden creada.
    """

    print(f"📝 Generando orden local para {tipo_estudio}...")

    # ------------------------------------
    # 1️⃣ Preparar payload para Edge Function
    # ------------------------------------
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

    files = {
        "payload": (None, json.dumps(payload), "application/json"),
    }

    if getattr(medico, "firma_medico", None):
        try:
            with open(medico.firma_medico.path, "rb") as f:
                files["firma_medico"] = ("firma.png", f.read(), "image/png")
        except Exception as e:
            print("⚠️ No se pudo leer la firma:", e)

    # ------------------------------------
    # 2️⃣ Ejecutar Edge Function → devuelve PDF real
    # ------------------------------------
    res = requests.post(SUPABASE_FUNCTION_URL, files=files)

    if res.status_code != 200:
        print("⚠️ Error generando PDF:", res.text)
        return None

    pdf_bytes = res.content

    # Validar PDF
    if not pdf_bytes.startswith(b"%PDF"):
        print("❌ ERROR: La Edge Function devolvió un archivo NO PDF")
        return None

    # ------------------------------------
    # 3️⃣ Guardar localmente en /media/ordenes/
    # ------------------------------------
    ordenes_dir = os.path.join(settings.MEDIA_ROOT, "ordenes")
    os.makedirs(ordenes_dir, exist_ok=True)

    fs = FileSystemStorage(location=ordenes_dir)

    tipo_clean = clean_filename(tipo_estudio)
    acomp_clean = clean_filename(str(acompañante))

    filename = f"orden_{consulta.id}_{tipo_clean}_pac_{paciente.id}_ac_{acomp_clean}.pdf"

    # Guardar PDF usando ContentFile (acepta bytes crudos)
    fs.save(filename, ContentFile(pdf_bytes))

    # ------------------------------------
    # 4️⃣ Crear URL ABSOLUTA (http://localhost:8000/media/ordenes/archivo.pdf)
    # ------------------------------------
    # Si no lo tenés en settings, agregalo:
    # SITE_URL = "http://localhost:8000"
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")

    file_url = f"{site_url}{settings.MEDIA_URL}ordenes/{filename}"

    # ------------------------------------
    # 5️⃣ Guardar registro en la base de datos
    # ------------------------------------
    orden = Orden.objects.create(
        primera_consulta=consulta,
        tipo_estudio=tipo_estudio,
        pdf_url=file_url,
    )

    print(f"✅ Orden guardada localmente en: {file_url}")

    return orden
