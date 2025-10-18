from django.db import models
class Estudio(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=50,
        choices=[
            ("ginecologico", "Ginecológico"),
            ("hormonal", "Hormonal"),
            ("semen", "Semen"),
            ("prequirurgico", "Prequirúrgico"),
        ]
    )
# Create your models here.
