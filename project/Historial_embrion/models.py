from django.db import models


class HistorialEmbrion(models.Model):
    embrion = models.ForeignKey(
        'Embrion.Embrion',
        on_delete=models.CASCADE,
        related_name='historial'
    )
    paciente = models.ForeignKey(
        'CustomUser.CustomUser',
        on_delete=models.CASCADE,
        related_name='historial_embriones',
        null=True
    )
    estado = models.CharField(max_length=100)
    calidad = models.CharField(max_length=50, null=True, blank=True)
    fecha = models.DateTimeField(auto_now=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    nota = models.TextField(blank=True, null=True)
    observaciones = models.TextField(null=True, blank=True)
    tipo_modificacion = models.CharField(max_length=100, null=True, blank=True)
    usuario = models.ForeignKey(
        'CustomUser.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='historial_embrion_registrado'
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial Embrion'
        verbose_name_plural = 'Historial Embriones'

    def __str__(self):
        try:
            embrion_ident = self.embrion.identificador
        except Exception:
            embrion_ident = str(self.embrion_id)
        return f"{embrion_ident} - {self.estado} @ {self.fecha}"

