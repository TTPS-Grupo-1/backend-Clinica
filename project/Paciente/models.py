from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, EmailValidator

solo_letras = RegexValidator(r'^[a-zA-ZáéíóúÁÉÍÓÚ\s]+$', 'Solo se permiten letras.')
solo_numeros = RegexValidator(r'^\d+$', 'Solo se permiten números.')

def validar_fecha_nacimiento(value):
    hoy = date.today()
    if value > hoy:
        raise ValidationError("La fecha de nacimiento no puede ser futura.")
    edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
    if edad < 18:
        raise ValidationError("El paciente debe ser mayor de 18 años.")

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente', null=True, blank=True)
    fecha_nacimiento = models.DateField(
        validators=[validar_fecha_nacimiento],
        blank=False
    )
    telefono = models.CharField(
        max_length=15,
        validators=[solo_numeros, MinLengthValidator(8, 'El teléfono debe tener al menos 8 dígitos.')],
        blank=False
    )
    obra_social = models.CharField(
        max_length=100,
        default='',
        blank=False
    )
    sexo = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=False
    )
    numero_afiliado = models.CharField(
        max_length=50,
        validators=[solo_numeros],
        blank=False
    )
    dni = models.CharField(
        max_length=20,
        unique=True,
        validators=[solo_numeros, MinLengthValidator(7, 'El DNI debe tener al menos 7 dígitos.')],
        blank=False
    )
    @property
    def nombre(self):
        return self.user.first_name if self.user else ''
    
    @property
    def apellido(self):
        return self.user.last_name if self.user else ''

    class Meta:
        db_table = 'Paciente'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

