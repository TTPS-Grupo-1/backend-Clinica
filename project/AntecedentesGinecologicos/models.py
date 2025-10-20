from django.db import models
from PrimerConsulta.models import PrimeraConsulta
class AntecedentesGinecologicos(models.Model):
    # Edad de la primera menstruación (menarca)
    menarca = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Edad en años de la primera menstruación (menarca)."
    )

    # Ciclo menstrual: duración típica del ciclo en días
    ciclo_menstrual = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Duración típica del ciclo menstrual en días (por ejemplo: 28)."
    )

    # Regularidad del ciclo
    REGULARIDAD_CHOICES = [
        ("regular", "Regular"),
        ("irregular", "Irregular"),
    ]
    regularidad = models.CharField(
        max_length=20,
        choices=REGULARIDAD_CHOICES,
        null=True,
        blank=True,
        help_text="Indica si los ciclos son regulares o irregulares."
    )

    # Duración del sangrado en días
    duracion_menstrual_dias = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Duración típica del sangrado menstrual en días."
    )

    # Características del sangrado
    CARACTERISTICAS_SANGRADO = [
        ("leve", "Leve"),
        ("moderado", "Moderado"),
        ("abundante", "Abundante"),
        ("intermitente", "Intermitente"),
    ]
    caracteristicas_sangrado = models.CharField(
        max_length=20,
        choices=CARACTERISTICAS_SANGRADO,
        null=True,
        blank=True,
        help_text="Características típicas del sangrado menstrual."
    )

    # G: cantidad total de embarazos (gravidez)
    g = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número total de embarazos (G)."
    )

    # P: número de partos a término
    p = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número de partos a término (P)."
    )

    # AB: cantidad de abortos
    ab = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número de abortos (AB)."
    )

    # ST: embarazos ectópicos (tubal/extrauterinos)
    st = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número de embarazos ectópicos (ST)."
    )
    
    consulta = models.ForeignKey(
			PrimeraConsulta,
			on_delete=models.CASCADE,
			related_name="antecedentes_ginecologicos"
	)

 
    def __str__(self):
        parts = [f"ID {self.id}"]
        if self.menarca:
            parts.append(f"menarca: {self.menarca}a")
        if self.ciclo_menstrual:
            parts.append(f"ciclo: {self.ciclo_menstrual}d")
        if self.g is not None:
            parts.append(f"G{self.g}")
        if self.p is not None:
            parts.append(f"P{self.p}")
        if self.ab is not None:
            parts.append(f"AB{self.ab}")
        return " | ".join(parts)
# Create your models here.
