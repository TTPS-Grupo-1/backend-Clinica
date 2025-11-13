from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError



class Transferencia(models.Model):
    """Representa una transferencia embrionaria asociada a un único tratamiento y a varios embriones."""
    tratamiento = models.ForeignKey(
       'Tratamiento.Tratamiento',
        on_delete=models.CASCADE,
        related_name='transferencias'
    )



    # Relación muchos-a-muchos mediante tabla intermedia. Cada Embrión solo
    # puede participar en una sola relación intermedia (OneToOne en la tabla
    # intermedia) garantizando que un embrión pertenezca a una sola transferencia,
    # pero una transferencia puede involucrar varios embriones.
    embriones = models.ManyToManyField(
        'Embrion.Embrion',
        through='TransferenciaEmbrion',
        related_name='transferencias',
        blank=True,
    )

    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transferencias_realizadas'
    )
    fecha = models.DateTimeField(null=True, blank=True)
    quirofano = models.CharField(max_length=120, blank=True, null=True)

    test_positivo = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transferencia'
        ordering = ['-created_at']
        # allow multiple Transferencia rows pointing to the same tratamiento (many embryos per treatment)

    def clean(self):
        # Ninguna validación por embrion aquí (se realiza en la tabla intermedia)
        return

    def save(self, *args, **kwargs):
        # run full validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transferencia #{self.id} - Tratamiento {self.tratamiento_id} - Embrión {self.embrion_id} - {self.created_at.date()}"


class TransferenciaEmbrion(models.Model):
    """Tabla intermedia que contiene la relación entre una Transferencia y un
    Embrion. Cada fila representa la participación de un embrión en una
    transferencia y almacena datos por-embrión (quién lo realizó, fecha,
    quirófano, resultado, observaciones).
    """
    transferencia = models.ForeignKey(
        Transferencia,
        on_delete=models.CASCADE,
        related_name='items_embrios'
    )

    
    embrion = models.OneToOneField(
        'Embrion.Embrion',
        on_delete=models.CASCADE,
        related_name='transferencia_item'
    )

    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transferencia_items_realizados'
    )

    fecha = models.DateTimeField(null=True, blank=True)
    quirofano = models.CharField(max_length=120, blank=True, null=True)

    # Resultado por embrión (por ejemplo test de implantación positivo)
    test_positivo = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transferencia_embrion'
        ordering = ['-created_at']

    def clean(self):
        # Validar que el embrión pertenezca a la paciente del tratamiento
        if getattr(self, 'transferencia', None) and getattr(self, 'embrion', None):
            try:
                emb = self.embrion
                if not getattr(emb, 'fertilizacion', None) or not getattr(emb.fertilizacion, 'ovocito', None):
                    raise ValidationError({'embrion': 'El embrión no tiene fertilización/ovocito asociado.'})
                emb_paciente = emb.fertilizacion.ovocito.paciente
                if emb_paciente.id != self.transferencia.tratamiento.paciente.id:
                    raise ValidationError({'embrion': 'El embrión no pertenece a la paciente del tratamiento.'})
            except AttributeError:
                raise ValidationError({'embrion': 'Error al validar el embrión.'})

    def save(self, *args, **kwargs):
        # Validaciones antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TransferenciaEmbrion #{self.id} - Transferencia {self.transferencia_id} - Embrión {self.embrion_id}"
