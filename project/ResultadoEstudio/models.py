from django.db import models
from PrimerConsulta.models import PrimeraConsulta


class ResultadoEstudio(models.Model):
    consulta = models.ForeignKey(PrimeraConsulta, on_delete=models.CASCADE, related_name="resultados_estudios")
    estudio_id_remoto = models.IntegerField()  # ID del estudio en la BD remota
    nombre_estudio = models.CharField(max_length=100)  # opcional: para cache/local display
    tipo = models.CharField(max_length=50, null=True, blank=True)  # opciona
    valor = models.CharField(max_length=255, blank=True, null=True)
# Create your models here.
