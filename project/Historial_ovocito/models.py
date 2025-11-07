from django.db import models


class HistorialOvocito(models.Model):
	"""Registro de eventos/estados asociados a un ovocito.

	Campos principales:
	- ovocito: FK a Ovocito.Ovocito
	- paciente: FK a CustomUser.CustomUser (propietario)
	- estado: texto corto indicando el estado
	- fecha: timestamp automático
	- nota: text opcional
	- usuario: FK al usuario que registró el evento
	"""

	id = models.AutoField(primary_key=True)
	ovocito = models.ForeignKey(
		'Ovocito.Ovocito',
		on_delete=models.CASCADE,
		related_name='historial',
		help_text='Ovocito al que pertenece este registro de historial'
	)
	paciente = models.ForeignKey(
		'CustomUser.CustomUser',
		on_delete=models.CASCADE,
		related_name='historial_ovocitos',
		help_text='Paciente propietario del ovocito'
	)

	estado = models.CharField(max_length=100, help_text='Estado registrado para el ovocito')
	fecha = models.DateTimeField(auto_now_add=True)
	nota = models.TextField(blank=True, null=True)
	usuario = models.ForeignKey(
		'CustomUser.CustomUser',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='historial_registrado',
		help_text='Usuario que registró el evento (medico/técnico)'
	)

	class Meta:
		verbose_name = 'Historial Ovocito'
		verbose_name_plural = 'Historial Ovocitos'
		ordering = ['-fecha']
		indexes = [
			models.Index(fields=['ovocito', 'paciente']),
			models.Index(fields=['fecha']),
		]

	def __str__(self) -> str:
		try:
			ov_ident = self.ovocito.identificador
		except Exception:
			ov_ident = str(self.ovocito_id)
		return f"{ov_ident} - {self.estado} @ {self.fecha}"
