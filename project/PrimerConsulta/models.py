from django.db import models

class PrimeraConsulta(models.Model):


    objetivo_consulta = models.TextField(null=True, blank=True)
    antecedentes_clinicos_1 = models.JSONField(null=True, blank=True)
    antecedentes_clinicos_2 = models.JSONField(null=True, blank=True)

    antecedentes_familiares_1 = models.TextField(null=True, blank=True)
    antecedentes_familiares_2 = models.TextField(null=True, blank=True)
    
    antecedentes_genitales = models.TextField(null=True, blank=True)

    

    antecedentes_quirurgicos_1 = models.TextField(null=True, blank=True)
    antecedentes_quirurgicos_2 = models.TextField(null=True, blank=True)

    examen_fisico_1 = models.TextField(null=True, blank=True)
    examen_fisico_2 = models.TextField(null=True, blank=True)
    

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Primera consulta de {self.paciente}"

    
# Create your models here.
