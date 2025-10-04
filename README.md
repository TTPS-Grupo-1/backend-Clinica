# 🧬 Backend - Clínica de Fertilidad Envy

> API REST desarrollada con **Django** y **Django REST Framework** para gestionar la lógica de negocio de la clínica de fertilidad.  
> Proyecto perteneciente a la materia *Taller de Tecnologías de Producción de Software - Opción Requerimientos*.

---

## ⚙️ Tecnologías

- Python 3.12+  
- Django 5+  
- Django REST Framework  
- SQLite (por defecto) o PostgreSQL  
- Virtualenv (venv)

---

## 🚀 Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPO>
cd <NOMBRE_DEL_PROYECTO>
````

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno

* **Windows**

  ```bash
  venv\Scripts\activate
  ```
* **Linux / macOS**

  ```bash
  source venv/bin/activate
  ```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear proyecto base (si aún no existe)

```bash
django-admin startproject clinica .
```

### 6. Ejecutar migraciones iniciales

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en navegador:

```
http://127.0.0.1:8000/
```

---

## 🧩 Estructura del proyecto

```
backend/
│
├── manage.py
│
├── clinica/                  # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Configuración global
│   ├── urls.py               # Enrutamiento principal
│   └── wsgi.py
│
└── pacientes/                # Ejemplo de aplicación
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    ├── models.py             # Modelos de base de datos
    ├── serializers.py        # Serializadores DRF
    ├── urls.py               # Rutas específicas
    ├── views.py              # Controladores / endpoints
    └── tests.py
```

---

## 🔗 Ejemplo de API con Django REST Framework

```python
# pacientes/models.py
from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateField()
```

```python
# pacientes/serializers.py
from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
```

```python
# pacientes/views.py
from rest_framework.viewsets import ModelViewSet
from .models import Paciente
from .serializers import PacienteSerializer

class PacienteViewSet(ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
```

```python
# clinica/urls.py
from django.urls import path, include
from rest_framework import routers
from pacientes.views import PacienteViewSet

router = routers.DefaultRouter()
router.register(r'pacientes', PacienteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

Ejemplo de endpoint:

```
GET  http://127.0.0.1:8000/api/pacientes/
```

---

## 🧾 Recomendaciones

* Crear una aplicación por dominio (ej. `pacientes`, `turnos`, `doctores`, `resultados`).

* Usar `django-cors-headers` para habilitar conexión con el frontend React:

  ```bash
  pip install django-cors-headers
  ```

  En `settings.py`:

  ```python
  INSTALLED_APPS += ['corsheaders']
  MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
  CORS_ALLOW_ALL_ORIGINS = True
  ```

* Mantener configuraciones sensibles en `.env` y fuera del repositorio.

* Para producción, usar `DEBUG=False` y configurar `ALLOWED_HOSTS`.

---

## 🧩 Comandos útiles

```bash
python manage.py startapp nombre_app     # Crear nueva app
python manage.py makemigrations          # Detectar cambios en modelos
python manage.py migrate                 # Aplicar migraciones
python manage.py createsuperuser         # Crear usuario admin
python manage.py runserver               # Ejecutar servidor
```

---


