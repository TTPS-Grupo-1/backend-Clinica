from django.db import models
from CustomUser.models import CustomUser
from PrimerConsulta.models import PrimeraConsulta
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
    motivo_finalizacion = models.TextField(
        blank=True,
        help_text="Motivo por el cual se finalizó el tratamiento"
    )
    objetivo = models.TextField(
        blank=True,
        help_text="Descripción detallada del tratamiento"
    )
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del tratamiento",
        auto_now_add=True
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


    primera_consulta = models.OneToOneField(
        PrimeraConsulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamiento',
        help_text="Primera consulta asociada al tratamiento"
    )
    segunda_consulta = models.OneToOneField(
        'SegundaConsulta.SegundaConsulta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamiento',
        help_text="Segunda consulta asociada al tratamiento"
    )
    transferencia = models.OneToOneField(
        'Transferencia.Transferencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferencia',
        help_text="Transferencia asociada al tratamiento"
    )
    puncion = models.OneToOneField(
        Puncion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='puncion',
        help_text="Punción asociada al tratamiento"
    )

    # Relación ManyToMany con Turnos
    turnos = models.ManyToManyField(
        Turno,
        related_name='tratamientos',
        help_text="Turnos asociados a este tratamiento"
    )
    
    id_pago = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID del pago asociado al tratamiento"
    )

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        # `nombre` no existe en este modelo; usar id y paciente para evitar AttributeError
        return f"Tratamiento #{self.id} - {self.paciente.get_full_name() or self.paciente.username}"
    
    @property
    def estado_actual(self):
        """
        Calcula y devuelve el estado actual del tratamiento basándose en los datos relacionados.
        Replica la lógica del frontend getEstadoTexto pero del lado del servidor.
        """
        # Si el tratamiento no está activo, está finalizado
        if not self.activo:
            return 'Finalizado'
        
        # Verificar si tiene seguimiento y está finalizado
        if hasattr(self, 'seguimiento_beta') and self.seguimiento_beta:
            return 'Finalizado'
        
        # Verificar si tiene transferencia
        if self.transferencia:
            return 'Transferencia'
        
        # Verificar si tiene fertilizaciones a través de la punción
        if self.puncion:
            # Importar aquí para evitar circular imports
            from Fertilizacion.models import Fertilizacion
            fertilizaciones = Fertilizacion.objects.filter(
                ovocito__puncion=self.puncion
            )
            if fertilizaciones.exists():
                return 'Fertilización'
        
        # Verificar si tiene punción
        if self.puncion:
            return 'Punción'
        
        # Verificar si tiene monitoreos
        monitoreos = self.lista_monitoreos.all()
        if monitoreos.exists():
            return 'Monitoreos'
        
        # Verificar si tiene segunda consulta
        if self.segunda_consulta:
            return 'Segunda consulta'
        
        # Verificar si tiene primera consulta
        if self.primera_consulta:
            return 'Primera consulta'
        
        # Estado por defecto si acaba de ser creado
        return 'En proceso'
