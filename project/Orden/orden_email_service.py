import requests
from django.template.loader import render_to_string
from django.conf import settings
from Orden.models import Orden


def enviar_ordenes_por_email(consulta):
    """
    Envía correo usando la API del módulo Avisos (send_email_v2)
    con links a los PDFs locales.
    """
    paciente = consulta.tratamiento.paciente
    email_destino = getattr(paciente, "email", None)

    if not email_destino:
        print("⚠️ Paciente sin email, no se envía aviso.")
        return False

    # Obtener todas las órdenes generadas
    ordenes = Orden.objects.filter(primera_consulta=consulta)
    if not ordenes.exists():
        print("⚠️ No hay órdenes para enviar.")
        return False

    # Render del HTML del cuerpo
    html_body = render_to_string(
        "ordenes_consultas.html",
        {
            "paciente": paciente,
            "consulta": consulta,
            "ordenes": ordenes,  # Cada una tiene un pdf_url ABSOLUTO
        }
    )

    # Llamar a la API externa
    url = "https://mvvuegssraetbyzeifov.supabase.co/functions/v1/send_email_v2"

    payload = {
        "group": 1,  # 🔥 Tu grupo
        "toEmails": [email_destino],
        "subject": f"Ordenes medicas - Primera Consulta",
        "htmlBody": html_body,
    }

    headers = {
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code == 200:
        print(f"✅ Email enviado a {email_destino}")
        return True

    print(f"❌ Error enviando email: {resp.status_code} → {resp.text}")
    return False
