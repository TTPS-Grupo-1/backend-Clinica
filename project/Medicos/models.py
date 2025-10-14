from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class Medico(models.Model):
    dni = models.IntegerField(unique=True, primary_key=True)  # 👈 Asegúrate de que sea primary_key o unique
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.IntegerField()
    password = models.CharField(max_length=128, default='')  # Campo para contraseña hasheada
    
    class Meta:
        db_table = 'medico'
    
    def save(self, *args, **kwargs):
        # Si la contraseña no está hasheada, hashearla
        if self.password and not self.password.startswith('bcrypt'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - DNI: {self.dni}"