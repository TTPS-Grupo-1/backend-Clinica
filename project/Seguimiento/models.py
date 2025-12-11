from django.db import models
from Tratamiento.models import Tratamiento 
from Transferencia.models import Transferencia
# Asegúrate de importar el modelo Transferencia, si está en otra app:
# from Transferencia.models import Transferencia 

class SeguimientoTratamiento(models.Model):
    """
    Modelo para registrar los resultados de seguimiento post-transferencia de embriones.
    """
    
    # RELACIÓN 1:1 con Tratamiento (sin cambios)
    tratamiento = models.OneToOneField(
        Tratamiento, 
        on_delete=models.CASCADE, 
        related_name='seguimiento_beta',
    )

    # ✅ NUEVO CAMPO: ID de Transferencia (Relación 1:1 o ForeignKey)
    # Si quieres que el seguimiento esté ligado a una transferencia específica:
    # Si cada tratamiento tiene una sola transferencia, OneToOneField.
    # Si un tratamiento puede tener varias, usa ForeignKey. Usaremos ForeignKey por flexibilidad.
    id_transferencia = models.ForeignKey(
        Transferencia, # Usa la referencia de string si el modelo está en otra app
        on_delete=models.SET_NULL, # Si se borra la transferencia, no se borra el seguimiento
        null=True,
        blank=True,
        help_text="Identificador de la transferencia de embriones a la que corresponde este seguimiento."
    )
    
    # 1. Resultado de la prueba Beta HCG (sin cambios)
    resultado_beta = models.BooleanField(
        default=False, 
        null=True, 
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
    
    # ✅ MODIFICACIÓN: Nacido vivo (Ahora por defecto NULL y no FALSE)
    nacido_vivo = models.BooleanField(
        default=None, # Por defecto es NULL (Pendiente de resultado)
        null=True,    # Permite NULL en la base de datos
        blank=True,   # Permite que el campo esté vacío en formularios
        help_text="Resultado final: True si el bebé nació vivo, False si no, NULL si está pendiente."
    )

    # ✅ NUEVO CAMPO: Cantidad de nacimientos
    cantidad_nacimientos = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Número de bebés nacidos vivos en este evento."
    )

    # ✅ NUEVO CAMPO: Fecha de nacimiento
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento del bebé/s."
    )

    # ✅ NUEVO CAMPO: Causa (Campo de texto libre opcional)
    causa = models.TextField(
        null=True,
        blank=True,
        help_text="Causa o explicación del resultado, especialmente si es negativo o hay complicaciones."
    )

    fecha_seguimiento = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Seguimiento de Resultado"
        verbose_name_plural = "Seguimiento de Resultados"
        
    def __str__(self):
        beta_status = "Positiva" if self.resultado_beta is True else ("Negativa" if self.resultado_beta is False else "Pendiente")
        return f"Seguimiento {self.tratamiento.id} - Beta: {beta_status}"