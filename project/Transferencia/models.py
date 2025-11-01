from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from Tratamiento.models import Tratamiento


class Transferencia(models.Model):
    """Representa una transferencia embrionaria asociada a un único tratamiento y a varios embriones."""
    tratamiento = models.ForeignKey(
        Tratamiento,
        on_delete=models.CASCADE,
        related_name='transferencias'
    )

    embriones = models.ManyToManyField('Embrion.Embrion', related_name='transferencias')

    test_positivo = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transferencia'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transferencia #{self.id} - Tratamiento {self.tratamiento_id} - {self.created_at.date()}"
