from django.db import models
from PrimerConsulta.models import PrimeraConsulta


class ResultadoEstudio(models.Model):
    PERSONA_CHOICES = [
        ("PACIENTE", "Paciente principal"),
        ("ACOMPAÑANTE", "Pareja / acompañante"),
    ]
    
    
    consulta = models.ForeignKey(PrimeraConsulta, on_delete=models.CASCADE, related_name="resultados_estudios")
    nombre_estudio = models.CharField(max_length=100)  # opcional: para cache/local display
    tipo_estudio = models.CharField(max_length=50, null=True, blank=True)  # opciona
    valor = models.CharField(max_length=255, blank=True, null=True)
    persona = models.CharField(max_length=20, choices=PERSONA_CHOICES, default="PACIENTE")
