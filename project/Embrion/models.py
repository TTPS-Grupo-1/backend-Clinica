from django.db import models
# Create your models here.
from django.utils import timezone

class Embrion(models.Model):
	identificador = models.CharField(max_length=50, unique=True, help_text="Identificador único del embrión (EMB...)")
	fecha_fertilizacion = models.DateField(help_text="Fecha de fertilización")
	ovocito = models.ForeignKey('Ovocito.Ovocito', on_delete=models.CASCADE, related_name="embriones", help_text="Ovocito relacionado")
	tecnica = models.CharField(max_length=100, help_text="Técnica utilizada")
	tecnico_laboratorio = models.CharField(max_length=100, help_text="Técnico de laboratorio responsable")
	calidad = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], help_text="Calidad del embrión (1-5)")
	estado = models.CharField(max_length=20, choices=[("transferido", "Transferido"), ("no_transferido", "No transferido")], help_text="Estado del embrión")
	fecha_alta = models.DateField(default=timezone.now, help_text="Fecha de alta")
	fecha_baja = models.DateField(null=True, blank=True, help_text="Fecha de baja")
	fecha_modificacion = models.DateTimeField(auto_now=True, help_text="Fecha de última modificación")
	info_semen = models.TextField(help_text="Información del semen")

	def __str__(self):
		return self.identificador

