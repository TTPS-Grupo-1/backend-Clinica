from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Embrion
from Historial_embrion.models import HistorialEmbrion

@receiver(post_save, sender=Embrion)
def registrar_historial_embrion(sender, instance, created, **kwargs):
    """
    Signal que registra en el historial cada vez que se crea o modifica un embrión
    """
    if created:
        # Es un embrión nuevo
        tipo_modificacion = "Creación del embrión"
    else:
        # Es una modificación
        tipo_modificacion = "Modificación del embrión"
    
    # Crear el registro en el historial
    HistorialEmbrion.objects.create(
        embrion=instance,
        estado=instance.estado,
        calidad=instance.calidad,
        observaciones=f"{tipo_modificacion}",
        tipo_modificacion=tipo_modificacion,
    )