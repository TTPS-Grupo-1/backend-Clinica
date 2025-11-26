from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from datetime import date

solo_numeros = RegexValidator(r'^\d+$', 'Solo se permiten números.')


# ---------------------------------------------------------
# MANAGER PERSONALIZADO
# ---------------------------------------------------------
class CustomUserManager(BaseUserManager):
    """
    Manager personalizado que usa email como identificador único.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


# ---------------------------------------------------------
# MODELO PRINCIPAL CUSTOMUSER
# ---------------------------------------------------------
class CustomUser(AbstractUser):
    """
    Usuario que unifica médicos, pacientes, administrativos, etc.
    Usa email como identificador único.
    """
    username = None  # Eliminamos username por completo
    email = models.EmailField(unique=True)

    ROL_CHOICES = [
        ('PACIENTE', 'Paciente'),
        ('MEDICO', 'Médico'),
        ('ADMIN', 'Administrativo'),
        ('OPERADOR_LABORATORIO', 'Operador de laboratorio'),
        ('DIRECTOR_MEDICO', 'Director Médico'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        help_text="Tipo de usuario dentro del sistema",
    )

    dni = models.CharField(
        max_length=20,
        unique=True,
        validators=[solo_numeros, MinLengthValidator(7, 'El DNI debe tener al menos 7 dígitos.')]
    )

    telefono = models.CharField(
        max_length=15,
        validators=[solo_numeros, MinLengthValidator(8, 'El teléfono debe tener al menos 8 dígitos.')],
        blank=True, null=True
    )

    eliminado = models.BooleanField(default=False)
    
    is_director = models.BooleanField(
        default=False,
    )

    # ---------------------------------------------------------
    # CAMPOS OPCIONALES SEGÚN ROL
    # ---------------------------------------------------------
    # Campos para PACIENTES
    fecha_nacimiento = models.DateField(null=True, blank=True)
    obra_social = models.BigIntegerField(blank=True, null=True)
    numero_afiliado = models.CharField(max_length=50, blank=True, null=True)
    sexo = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=True, null=True
    )

    # Campo para MÉDICOS
    firma_medico = models.ImageField(
        upload_to='firmas_medicos/',
        null=True, blank=True,
        help_text="Firma digital o escaneada del médico (PNG o JPG)"
    )

    # ---------------------------------------------------------
    # CONFIGURACIÓN DE AUTENTICACIÓN
    # ---------------------------------------------------------
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dni', 'first_name', 'last_name', 'rol']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rol})"

    # ---------------------------------------------------------
    # VALIDACIONES PERSONALIZADAS
    # ---------------------------------------------------------
    def clean(self):
        """
        Validaciones específicas según el tipo de rol.
        """
        if self.rol == 'PACIENTE' and not self.fecha_nacimiento:
            raise ValidationError("Los pacientes deben tener una fecha de nacimiento registrada.")
        if self.rol == 'MEDICO' and not self.firma_medico:
            # No es obligatorio, pero podés activar esto si querés exigirlo
            pass

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
