from django.db import models
from django.core.validators import MinLengthValidator
from .validators import validar_identificador
from CustomUser.models import CustomUser as Paciente


class Ovocito(models.Model):
	"""Modelo que representa un ovocito.
	Campos requeridos:
	- id_ovocito: AutoField autoincremental (PK)
	- identificador: string único
	- madurez: CharField con choices (sin usar Enum para compatibilidad SQLite)
	valores: 'muy_inmaduro', 'inmaduro', 'maduro'
	- tipo_estado: CharField con choices: 'fresco', 'criopreservado', 'descartado'
	"""

	id_ovocito = models.AutoField(primary_key=True)
	paciente = models.ForeignKey(
		Paciente,
		on_delete=models.CASCADE,
		related_name='ovocitos',
		help_text='Paciente al que pertenece el ovocito'
	)
	puncion = models.ForeignKey(
		'Puncion.Puncion',
		on_delete=models.CASCADE,
		related_name='ovocitos',
		null=True,
		blank=True,
		help_text='Punción asociada a este ovocito'
	)


	identificador = models.CharField(
		max_length=50,
		unique=True,
		validators=[validar_identificador, MinLengthValidator(3)],
		help_text='Identificador único del ovocito (3-50 chars, alfanum, _ o -)'
	)

	MADUREZ_MUY_INMADURO = 'muy_inmaduro'
	MADUREZ_INMADURO = 'inmaduro'
	MADUREZ_MADURO = 'maduro'

	MADUREZ_CHOICES = [
		(MADUREZ_MUY_INMADURO, 'Muy inmaduro'),
		(MADUREZ_INMADURO, 'Inmaduro'),
		(MADUREZ_MADURO, 'Maduro'),
	]

	madurez = models.CharField(max_length=20, choices=MADUREZ_CHOICES, default=MADUREZ_MUY_INMADURO)

	ESTADO_FRESCO = 'fresco'
	ESTADO_CRIOPRESERVADO = 'criopreservado'
	ESTADO_DESCARTADO = 'descartado'

	TIPO_ESTADO_CHOICES = [
		(ESTADO_FRESCO, 'Fresco'),
		(ESTADO_CRIOPRESERVADO, 'Criopreservado'),
		(ESTADO_DESCARTADO, 'Descartado'),
	]

	tipo_estado = models.CharField(max_length=20, choices=TIPO_ESTADO_CHOICES, default=ESTADO_FRESCO)


	def __str__(self) -> str:
		return f"{self.identificador} [{self.get_tipo_estado_display()}] ({self.get_madurez_display()})"

	class Meta:
		verbose_name = 'Ovocito'
		verbose_name_plural = 'Ovocitos'
		ordering = ['identificador']
