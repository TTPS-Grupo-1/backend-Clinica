from django.db import models


class Orden(models.Model):
    TIPO_ESTUDIO_CHOICES = [
        ("ginecologico", "Ginecológico"),
        ("hormonal", "Hormonal"),
        ("semen", "Semen"),
        ("prequirurgico", "Prequirúrgico"),
    ]

    primera_consulta = models.ForeignKey(
        "PrimerConsulta.PrimeraConsulta",
        on_delete=models.CASCADE,
        related_name="ordenes"
    )

    tipo_estudio = models.CharField(max_length=50, choices=TIPO_ESTUDIO_CHOICES)

    # 🔗 En lugar de guardar un FileField local, guardamos el enlace remoto
    pdf_url = models.URLField(max_length=500, null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden {self.id} - {self.get_tipo_estudio_display()}"
