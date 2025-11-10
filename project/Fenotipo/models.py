from django.db import models
from PrimerConsulta.models import PrimeraConsulta

class Fenotipo(models.Model):
	"""Modelo que representa características fenotípicas del paciente.

	Campos basados en el formulario: color de ojos, color de pelo, tipo de pelo,
	altura en centímetros, complexión corporal y rasgos étnicos generales.
	"""
	COMPLEXION_CHOICES = [
		("delgada", "Delgada"),
		("normal", "Normal"),
		("robusta", "Robusta"),
		("otra", "Otra"),
	]
 
	PERSONA_CHOICES = [
		("PACIENTE", "Paciente"),
		("ACOMPAÑANTE", "Acompañante"),
	]


	color_ojos = models.CharField(
		"color de ojos",
		max_length=64,
		blank=True,
		help_text="Ej: marrón, verde, azul",
	)

	color_pelo = models.CharField(
		"color de pelo",
		max_length=64,
		blank=True,
		help_text="Ej: rubio, castaño, negro",
	)

	tipo_pelo = models.CharField(
		"tipo de pelo",
		max_length=64,
		blank=True,
		help_text="Ej: lacio, ondulado, rizado",
	)

	altura_cm = models.PositiveSmallIntegerField(
		"altura (cm)",
		null=True,
		blank=True,
		help_text="Ej: 165",
	)

	complexion_corporal = models.CharField(
		"complexión corporal",
		max_length=16,
		choices=COMPLEXION_CHOICES,
		blank=True,
		default="normal",
	)

	rasgos_etnicos = models.TextField(
		"rasgos étnicos generales",
		blank=True,
		help_text="Ej: europeo, latino, afrodescendiente, etc.",
	)
 
	consulta = models.ForeignKey(
			PrimeraConsulta,
			on_delete=models.CASCADE,
			related_name="fenotipos"
	)
 
	persona = models.CharField(
		"persona",
		max_length=16,
		choices=PERSONA_CHOICES,
		default="PACIENTE",
	)
 
    

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		parts = []
		if self.color_ojos:
			parts.append(self.color_ojos)
		if self.color_pelo:
			parts.append(self.color_pelo)
		return " - ".join(parts) if parts else f"Fenotipo {self.pk}"

	class Meta:
		verbose_name = "Fenotipo"
		verbose_name_plural = "Fenotipos"
