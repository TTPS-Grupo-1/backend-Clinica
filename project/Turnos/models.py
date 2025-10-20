# Create your models here.
from django.db import models
from Medicos.models import Medico
from Paciente.models import Paciente

class Turno(models.Model):
    id = models.AutoField(primary_key=True)
    Paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos')
    Medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='turnos')
    fecha_hora = models.DateTimeField()

    class Meta:
        db_table = 'turno'
        ordering = ['fecha_hora']

    def __str__(self):
        return f"{self.paciente} - {self.medico} - {self.fecha_hora}"
