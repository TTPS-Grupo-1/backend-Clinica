from django.db import models

class SegundaConsulta(models.Model):
    
    
    ovocito_viable = models.BooleanField(default=False)
    semen_viable = models.BooleanField(default=False)
    consentimiento_informado = models.FileField(
        upload_to="consentimientos/",
        null=True,
        blank=True,
        help_text="Archivo PDF del consentimiento informado"
    )
    tipo_medicacion=models.CharField(max_length=255, null=True, blank=True)
    dosis_medicacion=models.CharField(max_length=255, null=True, blank=True)
    duracion_medicacion=models.CharField(max_length=255, null=True, blank=True)
    droga = models.CharField(max_length=255, null=True, blank=True)
    

    fecha = models.DateTimeField(auto_now_add=True)
    orden_droga_pdf = models.FileField(
        upload_to="ordenes_droga/",
        null=True,
        blank=True,
        help_text="Archivo PDF de la orden médica generada automáticamente"
    )


    def __str__(self):
        return f"Segunda consulta de {self.paciente}"
# Create your models here.
