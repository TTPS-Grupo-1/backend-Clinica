from django.db import models

class PrimeraConsulta(models.Model):
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='consultas'
    )

    medico = models.ForeignKey(
        'Medico',
        on_delete=models.SET_NULL,
        null=True,
        related_name='primeras_consultas_realizadas'
    )

    objetivo_consulta = models.TextField()

    antecedentes_familiares_1 = models.TextField()
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
