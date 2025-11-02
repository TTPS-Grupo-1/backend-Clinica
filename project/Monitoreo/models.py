from django.db import models


# Create your models here.
class Monitoreo(models.Model):
    """
    Modelo para registrar monitoreos de tratamientos.
    Se relaciona con Tratamiento, de donde se obtiene paciente y médico.
    """
    descripcion = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Descripción del monitoreo"
    )
    
    tratamiento = models.ForeignKey(
        'Tratamiento.Tratamiento',
        on_delete=models.CASCADE,
        related_name='lista_monitoreos',
        help_text="Tratamiento al que pertenece este monitoreo",
        null=True,  # ✅ CAMBIO: Permitir null temporalmente
        blank=True
    )
    
    atendido = models.BooleanField(
        default=False,
        help_text="Indica si el monitoreo ya fue atendido"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        help_text="Fecha de creación del monitoreo"
    )
    
    # ✅ CAMBIO: Fecha manual del turno donde se atenderá
    fecha_atencion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora del turno en que se atenderá este monitoreo"
    )
    
    fecha_realizado = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se atendió realmente el monitoreo"
    )

    
    class Meta:
        verbose_name = "Monitoreo"
        verbose_name_plural = "Monitoreos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        if self.tratamiento and self.paciente:
            estado = "Atendido" if self.atendido else "Pendiente"
            return f"Monitoreo {self.id} - {self.paciente.first_name} {self.paciente.last_name} - {estado}"
        return f"Monitoreo {self.id}"
    
    @property
    def paciente(self):
        """Obtiene el paciente desde el tratamiento"""
        return self.tratamiento.paciente if self.tratamiento else None
    
    @property
    def medico(self):
        """Obtiene el médico desde el tratamiento"""
        return self.tratamiento.medico if self.tratamiento else None
    
    @property
    def turno(self):
        """
        Obtiene el turno asociado a este monitoreo (si existe)
        Esto permite acceder al turno donde se atenderá el monitoreo
        """
        # TODO: Cuando exista la relación con Turno, implementar esto
        # return self.tratamiento.turnos.filter(fecha=self.fecha_atencion).first()
        return None
