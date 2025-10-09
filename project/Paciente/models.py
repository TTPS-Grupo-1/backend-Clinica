from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
from datetime import date
from django.core.exceptions import ValidationError

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
    nombre = models.CharField(
        max_length=100,
        validators=[solo_letras],
        default='',
        blank=False
    )
    apellido = models.CharField(
        max_length=100,
        validators=[solo_letras],
        default='',
        blank=False
    )
    fecha_nacimiento = models.DateField(
        validators=[validar_fecha_nacimiento],
        blank=False
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message='Debe ingresar un correo válido.')],
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
    contraseña = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(6, 'La contraseña debe tener al menos 6 caracteres.')],
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

    class Meta:
        db_table = 'Paciente'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

