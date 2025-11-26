# Turnos/models.py
from django.db import models
from CustomUser.models import CustomUser 

class Turno(models.Model):
    
    # Paciente: Clave foránea al usuario con rol 'PACIENTE'
    Paciente = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='turnos_paciente',
        limit_choices_to={'rol': 'PACIENTE'} # 💡 Opcional: Limita la búsqueda en el Admin
    )
    
    # Medico: Clave foránea al usuario con rol 'MEDICO'
    Medico = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='turnos_medico',
        limit_choices_to={'rol': 'MEDICO'} # 💡 Opcional: Limita la búsqueda en el Admin
    )
    
    # Campos de la Cita
    fecha_hora = models.DateTimeField() # Fecha y hora combinadas
    
    created_at = models.DateTimeField(auto_now_add=True)

    cancelado = models.BooleanField(default=False, help_text="Indica si el turno fue cancelado por el paciente o la clínica.")
    atendido = models.BooleanField(default=False, help_text="Indica si el turno ya fue completado y atendido por el médico.")
    id_externo = models.IntegerField(unique=True, help_text="ID único del turno en la API externa (Supabase).")
    es_monitoreo = models.BooleanField(default=False, help_text="Indica si el turno corresponde a un monitoreo.")

    class Meta:
        db_table = 'turno'
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Turno {self.id} con Dr. {self.Medico.last_name} - {self.fecha_hora}"