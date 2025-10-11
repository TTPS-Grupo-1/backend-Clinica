from django.db import models
from django.core.validators import MinLengthValidator
from .validators import validar_identificador
from Paciente.models import Paciente


class Ovocito(models.Model):
	"""Modelo que representa un ovocito.

	Campos requeridos:
	- id_ovocito: AutoField autoincremental (PK)
	- identificador: string único
	- estado: CharField con choices (sin usar Enum para compatibilidad SQLite)
	  valores: 'muy_inmaduro', 'inmaduro', 'maduro'
	- cripreservar: BooleanField
	"""

	id_ovocito = models.AutoField(primary_key=True)
	paciente = models.ForeignKey(
		Paciente,
		on_delete=models.CASCADE,
		related_name='ovocitos',
		help_text='Paciente al que pertenece el ovocito'
	)


	identificador = models.CharField(
		max_length=50,
		unique=True,
		validators=[validar_identificador, MinLengthValidator(3)],
		help_text='Identificador único del ovocito (3-50 chars, alfanum, _ o -)'
	)

	ESTADO_MUY_INMADURO = 'muy_inmaduro'
	ESTADO_INMADURO = 'inmaduro'
	ESTADO_MADURO = 'maduro'

	ESTADO_CHOICES = [
		(ESTADO_MUY_INMADURO, 'Muy inmaduro'),
		(ESTADO_INMADURO, 'Inmaduro'),
		(ESTADO_MADURO, 'Maduro'),
	]

	estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_MUY_INMADURO)

	cripreservar = models.BooleanField(default=False)

	descartado = models.BooleanField(default=False)


	def __str__(self) -> str:
		return f"{self.identificador} ({self.get_estado_display()})"

	class Meta:
		verbose_name = 'Ovocito'
		verbose_name_plural = 'Ovocitos'
		ordering = ['identificador']
