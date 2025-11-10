from django.db import models
# Create your models here.
from django.utils import timezone

class Embrion(models.Model):
	identificador = models.CharField(max_length=50, unique=True, help_text="Identificador único del embrión (EMB...)")

	fertilizacion = models.OneToOneField(
		'Fertilizacion.Fertilizacion',
		on_delete=models.CASCADE,
		related_name='embrion',
		null=True,
		help_text='Fertilización de la cual proviene este embrión'
	)
	

	
	calidad = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], help_text="Calidad del embrión (1-5)", blank=True, null=True)
	estado = models.CharField(max_length=20, choices=[("transferido", "Transferido"),("no transferido", "No Transferido"),("criopreservado", "Criopreservado"), ("descartado", "Descartado"), ("fresco", "Fresco")], help_text="Estado del embrión")
	fecha_modificacion = models.DateTimeField(auto_now=True, help_text="Fecha de última modificación")
	pgt = models.CharField(max_length=20, choices=[("exitoso", "Exitoso"), ("no exitoso", "No Exitoso")], default="no realizado", help_text="Resultado del PGT", blank=True, null=True)
	observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales sobre el embrión")
	fecha_baja = models.DateTimeField(blank=True, null=True, help_text="Fecha de baja del embrión")
	causa_descarte = models.TextField(blank=True, null=True, help_text="Causa de descarte del embrión")



	def __str__(self):
		return self.identificador

