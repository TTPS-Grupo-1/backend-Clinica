# 🏥 BACKEND CLÍNICA - ESTRUCTURA DEL PROYECTO

## 📁 ESTRUCTURA GENERAL

```
backend-Clinica/
├── 📄 README.md                    # Documentación principal del proyecto
├── 📄 requirements.txt             # Dependencias de Python
│
└── project/                        # 🎯 DIRECTORIO PRINCIPAL DE DJANGO
    ├── 📄 db.sqlite3              # Base de datos SQLite
    ├── 📄 manage.py               # Comando principal de Django
    │
    ├── project/                    # ⚙️ CONFIGURACIÓN DEL PROYECTO
    │   ├── __init__.py
    │   ├── asgi.py                # Configuración ASGI
    │   ├── settings.py            # 🔧 Configuraciones principales
    │   ├── urls.py                # 🌐 URLs principales del proyecto
    │   └── wsgi.py                # Configuración WSGI
    │
    └── Paciente/                   # 👤 APLICACIÓN DE PACIENTES
        ├── __init__.py
        ├── admin.py               # Configuración del panel de administración
        ├── apps.py                # Configuración de la aplicación
        ├── models.py              # 🗃️ MODELO DE DATOS
        ├── serializers.py         # 🔄 SERIALIZADORES (API)
        ├── tests.py               # 🧪 Pruebas unitarias
        ├── urls.py                # 🌐 URLs específicas de pacientes
        │
        ├── views/                  # 📋 VISTAS MODULARES
        │   ├── __init__.py
        │   ├── create_paciente_view.py      # ➕ Crear pacientes
        │   ├── update_paciente_view.py      # ✏️ Actualizar pacientes
        │   ├── delete_paciente_view.py      # 🗑️ Eliminar pacientes
        │   ├── list_paciente_view.py        # 📋 Listar pacientes
        │   └── main_viewset.py              # 🎯 ViewSet principal
        │
        └── migrations/             # 📦 MIGRACIONES DE BASE DE DATOS
            └── __init__.py
```

---

## 👤 MÓDULO PACIENTE - ESTRUCTURA DETALLADA

### 🗃️ **1. MODELO DE DATOS (`models.py`)**

```python
class Paciente(models.Model):
    # Campos principales
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)        # ⚠️ ÚNICO
    email = models.EmailField(unique=True)                   # ⚠️ ÚNICO
    telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
```

**Características importantes:**
- ✅ DNI y Email son únicos (no se pueden repetir)
- ✅ Validaciones automáticas de Django
- ✅ Fecha de creación automática

---

### 🔄 **2. SERIALIZADORES (`serializers.py`)**

```python
class PacienteSerializer(serializers.ModelSerializer):
    # Validaciones personalizadas
    def validate_email(self, value):
        # Verificar email único
    
    def validate_dni(self, value):
        # Verificar DNI único y formato
```

**Funciones:**
- 🔍 **Validación de datos** antes de guardar
- 🔄 **Conversión** entre JSON y modelos de Django
- ⚠️ **Mensajes de error personalizados**

---

### 📋 **3. VISTAS MODULARES (`views/`)**

#### 🎯 **`main_viewset.py`** - ViewSet Principal
```python
class PacienteViewSet(CreatePacienteMixin, UpdatePacienteMixin, 
                     DeletePacienteMixin, ListPacienteMixin, 
                     viewsets.ModelViewSet):
```
- 🎯 **Coordina todas las operaciones**
- 🔗 **Hereda de todos los mixins**
- 🌐 **Expone las APIs REST**

#### ➕ **`create_paciente_view.py`** - Crear Pacientes
```python
class CreatePacienteMixin:
    def create(self, request, *args, **kwargs):
        # Validar datos
        # Crear paciente
        # Manejar errores
```
- ✅ **Crear nuevos pacientes**
- ⚠️ **Validar unicidad** (email/DNI)
- 📝 **Mensajes personalizados**

#### ✏️ **`update_paciente_view.py`** - Actualizar Pacientes
```python
class UpdatePacienteMixin:
    def update(self, request, *args, **kwargs):
        # Actualizar datos existentes
```

#### 🗑️ **`delete_paciente_view.py`** - Eliminar Pacientes
```python
class DeletePacienteMixin:
    def destroy(self, request, *args, **kwargs):
        # Eliminar paciente
```

#### 📋 **`list_paciente_view.py`** - Listar Pacientes
```python
class ListPacienteMixin:
    def list(self, request, *args, **kwargs):
        # Obtener lista de pacientes
```

---

### 🌐 **4. URLs (`urls.py`)**

```python
urlpatterns = [
    path('api/pacientes/', PacienteViewSet.as_view({
        'get': 'list',       # GET    /api/pacientes/     → Listar
        'post': 'create',    # POST   /api/pacientes/     → Crear
    })),
    path('api/pacientes/<int:pk>/', PacienteViewSet.as_view({
        'get': 'retrieve',   # GET    /api/pacientes/1/   → Obtener uno
        'put': 'update',     # PUT    /api/pacientes/1/   → Actualizar
        'delete': 'destroy', # DELETE /api/pacientes/1/   → Eliminar
    })),
]
```

---

## 🔄 FLUJO DE DATOS

### ➕ **CREACIÓN DE PACIENTE**

```
1. 🌐 Frontend envía POST → /api/pacientes/
2. 🎯 main_viewset.py recibe la petición
3. 📋 create_paciente_view.py procesa la creación
4. 🔄 serializers.py valida los datos
5. 🗃️ models.py guarda en la base de datos
6. ✅ Respuesta JSON al frontend
```

### ⚠️ **MANEJO DE ERRORES**

```
❌ Error de validación → serializers.py
├── Email duplicado   → "Ya existe un paciente con este email"
├── DNI duplicado     → "Ya existe un paciente registrado con este DNI"
├── Campo requerido   → "Este campo es obligatorio"
└── Formato inválido  → "Formato incorrecto"
```

---

## 📡 APIS DISPONIBLES

| Método | Endpoint | Descripción | Vista |
|--------|----------|-------------|-------|
| `GET` | `/api/pacientes/` | 📋 Listar todos los pacientes | `list_paciente_view.py` |
| `POST` | `/api/pacientes/` | ➕ Crear nuevo paciente | `create_paciente_view.py` |
| `GET` | `/api/pacientes/{id}/` | 👁️ Obtener un paciente | `main_viewset.py` |
| `PUT` | `/api/pacientes/{id}/` | ✏️ Actualizar paciente | `update_paciente_view.py` |
| `DELETE` | `/api/pacientes/{id}/` | 🗑️ Eliminar paciente | `delete_paciente_view.py` |

---

## 🎯 VENTAJAS DE ESTA ESTRUCTURA

### ✅ **MODULARIDAD**
- Cada operación está en su propio archivo
- Fácil de encontrar y modificar código específico
- Separación clara de responsabilidades

### ✅ **MANTENIBILIDAD**
- Código organizado y legible
- Fácil testing de componentes individuales
- Escalabilidad para futuras funcionalidades

### ✅ **REUTILIZACIÓN**
- Los mixins se pueden usar en otros ViewSets
- Lógica compartida centralizada
- Patrones consistentes

---

## 🔧 CONFIGURACIÓN

### **settings.py**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'Paciente',  # ← Nuestra aplicación
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
```

### **urls.py principal**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Paciente.urls')),  # ← Incluir URLs de Paciente
]
```

---

## 🚀 CÓMO USAR

### **1. Iniciar servidor:**
```bash
cd project/
python manage.py runserver
```

### **2. Crear paciente (Frontend):**
```javascript
fetch('http://127.0.0.1:8000/api/pacientes/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        nombre: "Juan",
        apellido: "Pérez", 
        dni: "12345678",
        email: "juan@email.com",
        telefono: "1123456789",
        fecha_nacimiento: "1990-01-15"
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('✅', data.message);
    } else {
        console.log('❌', data.message);
        console.log('Errores:', data.errors);
    }
});
```

### **3. Respuestas típicas:**

**✅ Éxito:**
```json
{
    "success": true,
    "message": "Paciente registrado correctamente.",
    "data": { ...datos del paciente... }
}
```

**❌ Error:**
```json
{
    "success": false,
    "message": "Hay errores en los campos ingresados.",
    "errors": {
        "email": ["Ya existe un paciente registrado con este email."]
    }
}
```

---

## 📝 NOTAS IMPORTANTES

- 🔒 **Unicidad**: Email y DNI deben ser únicos
- 🔄 **Validación**: Se hace tanto en serializer como en modelo
- 📱 **API REST**: Sigue estándares REST para facilitar integración
- 🧪 **Testing**: Estructura preparada para pruebas unitarias
- 📈 **Escalabilidad**: Fácil agregar nuevas funcionalidades

---

*Este documento describe la estructura modular del backend de la clínica, diseñada para ser mantenible, escalable y fácil de entender.*
