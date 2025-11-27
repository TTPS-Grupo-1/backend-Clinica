from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Embrion
from Historial_embrion.models import HistorialEmbrion

@receiver(post_save, sender=Embrion)
def registrar_historial_embrion(sender, instance, created, **kwargs):
    """
    Signal que registra en el historial cada vez que se crea o modifica un embrión.
    Si el estado no cambió, actualiza la última fila en vez de crear una nueva.
    """
    if getattr(instance, '_skip_historial', False):
        return

    if created:
        tipo_modificacion = "Creación del embrión"
        HistorialEmbrion.objects.create(
            embrion=instance,
            estado=instance.estado,
            calidad=instance.calidad,
            observaciones=f"{tipo_modificacion}",
            tipo_modificacion=tipo_modificacion,
        )
    else:
        # Buscar el último historial de este embrión
        ultimo = HistorialEmbrion.objects.filter(embrion=instance).order_by('-id').first()
        if ultimo and ultimo.estado == instance.estado:
            # Solo actualiza la última fila si el estado no cambió
            ultimo.calidad = instance.calidad
            ultimo.observaciones = "Actualización de datos sin cambio de estado"
            ultimo.tipo_modificacion = "Modificación del embrión"
            ultimo.save()
        else:
            # Si el estado cambió, crea una nueva fila
            tipo_modificacion = "Modificación del embrión"
            HistorialEmbrion.objects.create(
                embrion=instance,
                estado=instance.estado,
                calidad=instance.calidad,
                observaciones=f"{tipo_modificacion}",
                tipo_modificacion=tipo_modificacion,
            )