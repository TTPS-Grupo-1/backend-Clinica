from django.db import models
from django.conf import settings


class Fertilizacion(models.Model):
	"""Modelo que representa una fertilización realizada sobre un ovocito.

	Campos principales:
	- id_fertilizacion: AutoField PK
	- ovocito: FK a Ovocito (requerido)
	- semen_info: texto opcional con identificador o notas del semen usado
	- semen_id: entero opcional (por si se integra una tabla externa de semen)
	- fecha_fertilizacion: fecha de la fertilización
	- tecnico: FK al usuario que registró (puede obtenerse de la sesión)
	- tecnica: elección (ICSI/FIV/etc)
	- resultado: elección (exitosa / no_exitosa)
	- notas: text
	- created_at: automatizado
	"""

	id_fertilizacion = models.AutoField(primary_key=True)
	ovocito = models.ForeignKey(
		'Ovocito.Ovocito',
		on_delete=models.CASCADE,
		related_name='fertilizaciones',
		help_text='Ovocito sobre el que se realizó la fertilización'
	)

	# Información del semen: campo libre y un posible id numérico si se integra otra tabla
	semen_info = models.CharField(max_length=150, null=True, blank=True, help_text='Identificador o notas del semen utilizado')
	semen_id = models.IntegerField(null=True, blank=True, help_text='ID del semen si existe una entidad externa')

	fecha_fertilizacion = models.DateField()

	# tecnico = models.ForeignKey(
	#     settings.AUTH_USER_MODEL,
	#     on_delete=models.SET_NULL,
	#     null=True,
	#     blank=True,
	#     related_name='fertilizaciones_registradas',
	#     help_text='Usuario (técnico) que registró la fertilización'
	# )
	tecnico_laboratorio = models.CharField(max_length=100, null=True, blank=True, help_text='Nombre del técnico que registró la fertilización')

	# Técnica representada como dos booleanos (uno debe ser True)
	tecnica_icsi = models.BooleanField(default=False, help_text='True si la técnica fue ICSI')
	tecnica_fiv = models.BooleanField(default=False, help_text='True si la técnica fue FIV')

	RESULTADO_EXITOSA = 'exitosa'
	RESULTADO_NO_EXITOSA = 'no_exitosa'
	RESULTADO_CHOICES = [
		(RESULTADO_EXITOSA, 'Exitosa'),
		(RESULTADO_NO_EXITOSA, 'No exitosa'),
	]
	resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default=RESULTADO_NO_EXITOSA)

	notas = models.TextField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'fertilizacion'
		ordering = ['-fecha_fertilizacion', '-created_at']

	def __str__(self) -> str:
		return f"Fertilización #{self.id_fertilizacion} - Ovocito {self.ovocito} - {self.get_resultado_display()}"

	@property
	def is_exitosa(self) -> bool:
		return self.resultado == self.RESULTADO_EXITOSA

	def clean(self):
		# Validación: exactamente una de las técnicas debe ser True
		from django.core.exceptions import ValidationError
		tecnica_sum = int(bool(self.tecnica_icsi)) + int(bool(self.tecnica_fiv))
		if tecnica_sum != 1:
			raise ValidationError('Debe indicarse exactamente una técnica: ICSI o FIV')

