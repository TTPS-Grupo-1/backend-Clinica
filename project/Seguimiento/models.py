# Seguimiento/models.py (o Tratamiento/models.py)

from django.db import models
from Tratamiento.models import Tratamiento 

class SeguimientoTratamiento(models.Model):
    """
    Modelo para registrar los resultados de seguimiento post-transferencia de embriones,
    utilizando campos booleanos (True=1 / False=0) para todos los resultados.
    """
    tratamiento = models.OneToOneField(
        Tratamiento, 
        on_delete=models.CASCADE, 
        related_name='seguimiento_beta',
    )
    
    # 1. Resultado de la prueba Beta HCG (Boolean: True=Positiva, False=Negativa)
    # Se hace null=True para poder representar el estado "Pendiente/No realizado" si es necesario.
    resultado_beta = models.BooleanField(
        default=False, 
        null=True, # Permite NULL en la BD para distinguir entre "No realizado" y "Negativa"
        help_text="Resultado de la prueba Beta HCG (True=Positiva, False=Negativa)."
    )
    
    # 2. Desarrollo del Embarazo (Booleanos puros)
    hay_saco_gestacional = models.BooleanField(
        default=False,
        help_text="Confirmación de saco gestacional mediante ecografía."
    )
    
    embarazo_clinico = models.BooleanField(
        default=False,
        help_text="Confirmación de latido cardíaco fetal (define embarazo clínico)."
    )
    
    nacido_vivo = models.BooleanField(
        default=False,
        help_text="Resultado final: indica si el bebé nació vivo."
    )

    fecha_seguimiento = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Seguimiento de Resultado"
        verbose_name_plural = "Seguimiento de Resultados"
        
    def __str__(self):
        beta_status = "Positiva" if self.resultado_beta is True else ("Negativa" if self.resultado_beta is False else "Pendiente")
        return f"Seguimiento {self.tratamiento.id} - Beta: {beta_status}"