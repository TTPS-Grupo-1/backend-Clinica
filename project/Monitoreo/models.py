from django.db import models
from CustomUser.models import CustomUser


# Create your models here.
class Monitoreo(models.Model):
    descripcion = models.CharField(max_length=500, help_text="Descripción del monitoreo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del monitoreo")
    fecha_atencion = models.DateTimeField(auto_now=True, help_text="Fecha de atención del monitoreo")
    atendido = models.BooleanField(default=False, help_text="Indica si el monitoreo ha sido atendido")
    
    tratamiento = models.ForeignKey(
        'Tratamiento.Tratamiento',  # 👈 Cuando tus compañeros creen la app
        on_delete=models.CASCADE,
        related_name='monitoreos',
        help_text="Tratamiento al que pertenece este monitoreo",
        null=True,  # 👈 Temporal mientras no exista Tratamiento
        blank=True  # 👈 Temporal mientras no exista Tratamiento
    )

    def __str__(self):
        return f"Monitoreo {self.id} - Paciente: {self.paciente.first_name} {self.paciente.last_name} - Médico: {self.medico.first_name} {self.medico.last_name}"


    @property
    def paciente(self):
        """Obtiene el paciente desde el tratamiento"""
        return self.tratamiento.paciente if self.tratamiento else None
    
    @property
    def medico(self):
        """Obtiene el médico desde el tratamiento"""
        return self.tratamiento.medico if self.tratamiento else None