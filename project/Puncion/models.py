from django.db import models
from CustomUser.models import CustomUser as Paciente

class Puncion(models.Model):
	paciente = models.ForeignKey(
		Paciente,
		on_delete=models.CASCADE,
		related_name='punciones',
		help_text='Paciente al que pertenece la punción'
	)
	fecha = models.DateField()
	quirofano = models.CharField(max_length=50)
	# otros campos relevantes

	def __str__(self):
		return f"Punción de {self.paciente} en {self.quirofano} el {self.fecha}"

	class Meta:
		verbose_name = 'Punción'
		verbose_name_plural = 'Punciones'
		ordering = ['-fecha']
