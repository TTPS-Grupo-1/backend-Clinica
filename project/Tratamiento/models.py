from django.db import models
from CustomUser.models import CustomUser
from PrimerConsulta.models import PrimeraConsulta
from Transferencia.models import Transferencia
from Puncion.models import Puncion
from Turnos.models import Turno
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

    
    primera_consulta = models.ForeignKey(
        PrimeraConsulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamientos',
        help_text="Primera consulta asociada al tratamiento"
    )
    transferencia = models.ForeignKey(
        Transferencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferencias',
        help_text="Transferencia asociada al tratamiento"
    )
    puncion = models.ForeignKey(
        Puncion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='punciones',
        help_text="Punción asociada al tratamiento"
    )

    # Relación ManyToMany con Turnos
    turnos = models.ManyToManyField(
        Turno,
        related_name='tratamientos',
        help_text="Turnos asociados a este tratamiento"
    )

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.paciente.get_full_name() or self.paciente.username}"
