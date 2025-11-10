from django.db import models
from PrimerConsulta.models import PrimeraConsulta

class AntecedentesPersonales(models.Model):
	"""Modelo para antecedentes personales relacionados con hábitos.

	Campos según el formulario: fuma (pack-días), consume alcohol (frecuencia y tipo),
	drogas recreativas, observaciones sobre hábitos.
	"""

	# pack-días: se permite decimal (por ejemplo 2.5)
	fuma_pack_dias = models.CharField(
		"fuma (pack-días)",
		max_length=6,
		null=True,
		blank=True,
		help_text="Ej: 10 cigarrillos/día * 5 años / 20 = 2.5",
	)

	consume_alcohol = models.CharField(
		"consume alcohol (frecuencia y tipo)",
		max_length=255,
		blank=True,
		help_text="Ej: 2 veces por semana, cerveza",
	)

	drogas_recreativas = models.CharField(
		"drogas recreativas",
		max_length=255,
		blank=True,
		help_text="Ej: marihuana ocasional",
	)

	observaciones_habitos = models.TextField(
		"observaciones sobre hábitos",
		blank=True,
		help_text="Observaciones libres sobre hábitos",
	)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
	consulta = models.ForeignKey(
			PrimeraConsulta,
			on_delete=models.CASCADE,
			related_name="antecedentes_personales"
	)

	def __str__(self):
		if self.fuma_pack_dias:
			return f"Fuma: {self.fuma_pack_dias} pack-días"
		if self.consume_alcohol:
			return f"Alcohol: {self.consume_alcohol}"
		return f"AntecedentesPersonales {self.pk}"

	class Meta:
		verbose_name = "Antecedente personal"
		verbose_name_plural = "Antecedentes personales"
