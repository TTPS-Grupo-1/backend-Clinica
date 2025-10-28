from django.db import models
from CustomUser.models import CustomUser


# Create your models here.
class Monitoreo(models.Model):
    descripcion = models.CharField(max_length=500, help_text="Descripción del monitoreo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del monitoreo")
    fecha_modificacion = models.DateTimeField(auto_now=True, help_text="Fecha de última modificación del monitoreo")
    segunda_consulta = models.ForeignKey(
        'SegundaConsulta.SegundaConsulta',
        on_delete=models.CASCADE,
        related_name='monitoreos',
        help_text="Segunda consulta asociada al monitoreo"
    )
    

    def __str__(self):
        return f"Monitoreo {self.id} - Descripción: {self.descripcion}"


