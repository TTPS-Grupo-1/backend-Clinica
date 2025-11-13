from django.db import models



class HistorialEmbrion(models.Model):
	"""Registro de eventos/estados asociados a un embrion.

	"""

	id = models.AutoField(primary_key=True)
	embrion = models.ForeignKey(
		'Embrion.Embrion',
		on_delete=models.CASCADE,
		related_name='historial',
		help_text='Embrion al que pertenece este registro de historial'
	)
	paciente = models.ForeignKey(
		'CustomUser.CustomUser',
		on_delete=models.CASCADE,
		related_name='historial_embriones',
		help_text='Paciente propietario del embrion'
	)

	estado = models.CharField(max_length=100, help_text='Estado registrado para el embrion')
	fecha = models.DateTimeField(auto_now_add=True)
	nota = models.TextField(blank=True, null=True)
	usuario = models.ForeignKey(
		'CustomUser.CustomUser',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='historial_embrion_registrado',
		help_text='Usuario que registró el evento (medico/técnico)'
	)

	class Meta:
		verbose_name = 'Historial Embrion'
		verbose_name_plural = 'Historial Embriones'
		ordering = ['-fecha']
		indexes = [
			models.Index(fields=['embrion', 'paciente']),
			models.Index(fields=['fecha']),
		]

	def __str__(self) -> str:
		try:
			embrion_ident = self.embrion.identificador
		except Exception:
			embrion_ident = str(self.embrion_id)
		return f"{embrion_ident} - {self.estado} @ {self.fecha}"

