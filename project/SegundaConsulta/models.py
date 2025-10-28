from django.db import models

class SegundaConsulta(models.Model):
    
    primera_consulta = models.OneToOneField(
        'PrimerConsulta.PrimeraConsulta',
        on_delete=models.CASCADE,
        null=True,
        related_name='segunda_consulta'
    )
    
    ovocito_viable = models.BooleanField(default=False)
    semen_viable = models.BooleanField(default=False)
    consentimiento_informado = models.BinaryField(null=True, blank=True)
    tipo_medicacion=models.CharField(max_length=255, null=True, blank=True)
    dosis_medicacion=models.CharField(max_length=255, null=True, blank=True)
    duracion_medicacion=models.CharField(max_length=255, null=True, blank=True)
    

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Segunda consulta de {self.paciente}"
# Create your models here.
