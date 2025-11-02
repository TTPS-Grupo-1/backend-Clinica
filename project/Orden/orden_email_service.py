from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from Orden.models import Orden

def enviar_ordenes_por_email(consulta):
    """
    Envía todas las órdenes generadas para una PrimeraConsulta al paciente.
    """
    paciente = consulta.tratamiento.paciente
    email_paciente = getattr(paciente, "email", None)

    if not email_paciente:
        print("⚠️ Paciente sin email registrado, no se envía correo.")
        return False

    # Obtener todas las órdenes de esa consulta
    ordenes = Orden.objects.filter(primera_consulta=consulta)
    if not ordenes.exists():
        print("⚠️ No hay órdenes para enviar.")
        return False

    # Crear cuerpo HTML
    html_message = render_to_string("ordenes_consultas.html", {
        "paciente": paciente,
        "consulta": consulta,
        "ordenes": ordenes,
    })

    subject = f"Órdenes médicas - Consulta #{consulta.id}"
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_paciente],
    )

    email.content_subtype = "html"

    # Adjuntar PDFs (si querés incluirlos como adjuntos)
    for orden in ordenes:
        try:
            import requests
            response = requests.get(orden.pdf_url)
            if response.status_code == 200:
                file_name = orden.pdf_url.split("/")[-1]
                email.attach(file_name, response.content, "application/pdf")
        except Exception as e:
            print(f"⚠️ No se pudo adjuntar {orden.pdf_url}: {e}")

    email.send()
    print(f"✅ Correo enviado correctamente a {email_paciente}")
    return True
