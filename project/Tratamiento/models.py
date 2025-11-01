from django.db import models
from CustomUser.models import CustomUser
from Monitoreo.models import Monitoreo
from PrimerConsulta.models import PrimeraConsulta


class Tratamiento(models.Model):
    """
    Modelo que representa un tratamiento de fertilidad asignado a un paciente.
    """
    paciente = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='tratamientos',
        limit_choices_to={'rol': 'paciente'},
        help_text="Paciente al que se le asigna este tratamiento"
    )
    objetivo = models.TextField(
        blank=True,
        help_text="Descripción detallada del tratamiento"
    )
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del tratamiento"
    )
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tratamientos_asignados',
        limit_choices_to={'rol': 'MEDICO'},
        help_text="Médico responsable del tratamiento"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el tratamiento está activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # New nullable foreign keys
    monitoreo = models.ForeignKey(
        Monitoreo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamientos',
        help_text="Monitoreo asociado al tratamiento"
    )
    primera_consulta = models.ForeignKey(
        PrimeraConsulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamientos',
        help_text="Primera consulta asociada al tratamiento"
    )

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.paciente.get_full_name() or self.paciente.username}"
