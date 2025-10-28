from django.db import models
from CustomUser.models import CustomUser


# Create your models here.
class Monitoreo(models.Model):
    descripcion = models.CharField(max_length=500, help_text="Descripción del monitoreo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del monitoreo")
    fecha_modificacion = models.DateTimeField(auto_now=True, help_text="Fecha de última modificación del monitoreo")
    numero_monitoreos = models.IntegerField(help_text="Número de monitoreos realizados")
    
    paciente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='monitoreos_como_paciente',
        limit_choices_to={'rol': 'PACIENTE'},
        help_text='Paciente al que pertenece el monitoreo'
    )

    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='monitoreos_como_medico',
        limit_choices_to={'rol': 'MEDICO'},
        help_text='Médico responsable del monitoreo'
    )

    def __str__(self):
        return f"Monitoreo {self.id} - Paciente: {self.paciente.first_name} {self.paciente.last_name} - Médico: {self.medico.first_name} {self.medico.last_name}"


