from django.db import models
from PrimerConsulta.models import PrimeraConsulta
from Estudio.models import Estudio

class ConsultaEstudio(models.Model):
    consulta = models.ForeignKey(PrimeraConsulta, on_delete=models.CASCADE)
    estudio = models.ForeignKey(Estudio, on_delete=models.CASCADE)
    valor = models.CharField(max_length=255, blank=True, null=True)
# Create your models here.
