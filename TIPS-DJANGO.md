# 🐍 TIPS DJANGO - Guía Completa

## 📋 Tabla de Contenidos
- [Comandos de Migraciones](#-comandos-de-migraciones)
- [Estructura de una App Django](#-estructura-de-una-app-django)
- [Mejores Prácticas](#-mejores-prácticas)
- [Comandos Útiles](#-comandos-útiles)

---

## 🔄 Comandos de Migraciones

### Cuándo usar cada comando:

#### 1. `python manage.py makemigrations`
**¿Cuándo usarlo?**
- Después de crear o modificar modelos en `models.py`
- Cuando agregues, elimines o cambies campos
- Cuando modifiques opciones de modelo (Meta class)

```bash
# Generar migraciones para todos los cambios
python manage.py makemigrations

# Generar migraciones solo para una app específica
python manage.py makemigrations nombre_app

# Generar migración con nombre personalizado
python manage.py makemigrations --name agregar_campo_email nombre_app

# Ver qué migraciones se generarían sin crearlas
python manage.py makemigrations --dry-run
```

#### 2. `python manage.py migrate`
**¿Cuándo usarlo?**
- Después de `makemigrations` para aplicar los cambios a la BD
- Al configurar un proyecto por primera vez
- Después de hacer `git pull` si hay nuevas migraciones

```bash
# Aplicar todas las migraciones pendientes
python manage.py migrate

# Aplicar migraciones de una app específica
python manage.py migrate nombre_app

# Migrar a una migración específica
python manage.py migrate nombre_app 0001_initial

# Ver qué migraciones se aplicarían
python manage.py migrate --plan
```

#### 3. `python manage.py showmigrations`
**¿Cuándo usarlo?**
- Para ver el estado de las migraciones
- Para debuggear problemas de migración

```bash
# Ver todas las migraciones y su estado
python manage.py showmigrations

# Ver migraciones de una app específica
python manage.py showmigrations nombre_app
```

#### 4. `python manage.py sqlmigrate`
**¿Cuándo usarlo?**
- Para ver el SQL que generará una migración
- Para debuggear problemas complejos

```bash
# Ver el SQL de una migración específica
python manage.py sqlmigrate nombre_app 0001
```

---

## 📁 Estructura de una App Django

Cuando ejecutas `python manage.py startapp nombre_app`, se generan estos archivos:

### 📄 `__init__.py`
```python
# Archivo vacío que hace que Python trate el directorio como un paquete
# Generalmente no necesitas modificarlo
```

### 📄 `admin.py`
**Propósito:** Configurar la interfaz de administración de Django

```python
from django.contrib import admin
from .models import Paciente

# Registro básico
admin.site.register(Paciente)

# Registro avanzado con personalización
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'dni', 'fecha_nacimiento']
    list_filter = ['fecha_nacimiento']
    search_fields = ['nombre', 'apellido', 'dni']
    ordering = ['apellido', 'nombre']
    readonly_fields = ['fecha_creacion']
```

### 📄 `apps.py`
**Propósito:** Configuración de la aplicación

```python
from django.apps import AppConfig

class PacienteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Paciente'  # Debe coincidir con el nombre del directorio
    verbose_name = 'Gestión de Pacientes'  # Nombre en el admin
    
    def ready(self):
        # Código que se ejecuta cuando la app está lista
        import Paciente.signals  # Para signals
```

### 📄 `models.py`
**Propósito:** Definir los modelos de datos (tablas de BD)

```python
from django.db import models
from django.core.validators import RegexValidator

class Paciente(models.Model):
    # Campos básicos
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    # Campo único con validación
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', 'DNI debe tener 8 dígitos')]
    )
    
    # Campos de fecha
    fecha_nacimiento = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Opciones del modelo
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']
        db_table = 'pacientes'  # Nombre personalizado de tabla
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
    
    def edad(self):
        from datetime import date
        return date.today().year - self.fecha_nacimiento.year
```

### 📄 `views.py`
**Propósito:** Lógica de las vistas (controladores)

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Paciente
from .serializers import PacienteSerializer

# ViewSet completo para CRUD
class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    
    # Acción personalizada
    @action(detail=True, methods=['get'])
    def edad(self, request, pk=None):
        paciente = self.get_object()
        return Response({'edad': paciente.edad()})
    
    # Sobrescribir create para logging
    def create(self, request, *args, **kwargs):
        print(f"Creando paciente con datos: {request.data}")
        return super().create(request, *args, **kwargs)

# Vista basada en función (alternativa)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def crear_paciente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Lógica para crear paciente
        return JsonResponse({'status': 'created'})
```

### 📄 `serializers.py`
**Propósito:** Serialización para APIs (Django REST Framework)

```python
from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    # Campo calculado
    edad = serializers.SerializerMethodField()
    
    class Meta:
        model = Paciente
        fields = '__all__'  # O especificar: ['id', 'nombre', 'apellido', ...]
        read_only_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_edad(self, obj):
        return obj.edad()
    
    # Validación personalizada
    def validate_dni(self, value):
        if len(value) != 8:
            raise serializers.ValidationError("DNI debe tener 8 dígitos")
        return value
    
    # Validación de múltiples campos
    def validate(self, data):
        # Lógica de validación compleja
        return data

# Serializer anidado para relaciones
class PacienteDetalleSerializer(serializers.ModelSerializer):
    turnos = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Paciente
        fields = '__all__'
```

### 📄 `urls.py`
**Propósito:** Definir las rutas de la aplicación

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Con Router (DRF)
router = DefaultRouter()
router.register(r'pacientes', views.PacienteViewSet)

# URLs de la app
app_name = 'paciente'  # Namespace
urlpatterns = [
    # Incluir rutas del router
    path('api/', include(router.urls)),
    
    # Rutas manuales
    path('crear/', views.crear_paciente, name='crear_paciente'),
    path('listado/', views.listado_pacientes, name='listado'),
]

# En el urls.py principal del proyecto:
# path('', include('Paciente.urls')),
```

### 📄 `tests.py`
**Propósito:** Pruebas unitarias y de integración

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Paciente

class PacienteModelTest(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            fecha_nacimiento="1990-01-01"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.paciente), "Pérez, Juan")
    
    def test_edad_calculation(self):
        # Test del método edad
        self.assertGreater(self.paciente.edad(), 0)

class PacienteAPITest(APITestCase):
    def test_crear_paciente(self):
        data = {
            'nombre': 'Ana',
            'apellido': 'García',
            'dni': '87654321',
            'fecha_nacimiento': '1985-05-15'
        }
        response = self.client.post('/api/pacientes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Paciente.objects.count(), 1)
```

### 📁 `migrations/`
**Propósito:** Historial de cambios en la base de datos

```python
# migrations/0001_initial.py (generado automáticamente)
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
    ]
    
    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                # ... otros campos
            ],
        ),
    ]
```

---

## ⭐ Mejores Prácticas

### 🔄 Migraciones
```bash
# ✅ Flujo correcto
1. Modificar models.py
2. python manage.py makemigrations
3. Revisar el archivo de migración generado
4. python manage.py migrate

# ❌ Errores comunes
- Modificar archivos de migración manualmente
- Hacer migrate sin makemigrations
- Eliminar archivos de migración
- No hacer backup antes de migraciones complejas
```

### 📂 Organización de Apps
```bash
# ✅ Una app por funcionalidad
pacientes/     # Gestión de pacientes
turnos/        # Sistema de turnos
doctores/      # Gestión de médicos
facturas/      # Sistema de facturación

# ❌ Apps muy grandes
todo_el_sistema/  # Evitar apps monolíticas
```

### 🔧 Configuración
```python
# settings.py - Orden recomendado en INSTALLED_APPS
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'Paciente',
    'Turnos',
]
```

---

## 🛠️ Comandos Útiles

### Desarrollo
```bash
# Crear proyecto
django-admin startproject nombre_proyecto

# Crear app
python manage.py startapp nombre_app

# Servidor de desarrollo
python manage.py runserver
python manage.py runserver 8080  # Puerto personalizado

# Shell interactivo
python manage.py shell

# Crear superusuario
python manage.py createsuperuser
```

### Base de Datos
```bash
# Ver SQL de migraciones
python manage.py sqlmigrate app_name migration_name

# Migración fake (marcar como aplicada sin ejecutar)
python manage.py migrate --fake app_name migration_name

# Revertir migración
python manage.py migrate app_name 0001  # Volver a migración específica
python manage.py migrate app_name zero  # Revertir todas
```

### Debugging
```bash
# Verificar configuración
python manage.py check

# Verificar configuración de BD
python manage.py check --database default

# Mostrar configuración
python manage.py diffsettings

# Limpiar sesiones expiradas
python manage.py clearsessions
```

### Datos
```bash
# Crear fixtures (backup de datos)
python manage.py dumpdata app_name > fixture.json

# Cargar fixtures
python manage.py loaddata fixture.json

# SQL para reset de auto-increment
python manage.py sqlflush
```

---

## 🐛 Solución de Problemas Comunes

### Error: "No migrations to apply"
```bash
# Verificar estado
python manage.py showmigrations

# Recrear migraciones
python manage.py makemigrations --empty app_name
```

### Error: "Table already exists"
```bash
# Migración fake
python manage.py migrate --fake-initial
```

### Error: "App not in INSTALLED_APPS"
```python
# Agregar en settings.py
INSTALLED_APPS = [
    # ...
    'nombre_app',
]
```

---

## 📚 Recursos Adicionales

- [Documentación oficial de Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Packages](https://djangopackages.org/)

---

**💡 Tip:** Siempre haz backup de tu base de datos antes de ejecutar migraciones en producción!
