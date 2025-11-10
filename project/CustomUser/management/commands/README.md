# 🌱 Seeds para la Clínica de Fertilidad

Este directorio contiene comandos de Django para poblar la base de datos con datos de ejemplo para desarrollo y testing.

## 📋 Comandos Disponibles

### 1. Seed de Médicos Solamente
```bash
python manage.py seed_medicos
```

**Opciones:**
- `--clear`: Elimina médicos existentes antes de crear nuevos
```bash
python manage.py seed_medicos --clear
```

**Crea:**
- 5 médicos especialistas en fertilidad
- 1 director médico
- Todos con contraseñas por defecto

### 2. Seed Completo de Usuarios
```bash
python manage.py seed_users
```

**Opciones:**
- `--clear`: Elimina usuarios existentes (excepto superusers)
- `--only [medicos|pacientes|admin]`: Crea solo un tipo específico

```bash
# Crear solo médicos
python manage.py seed_users --only medicos

# Crear solo pacientes
python manage.py seed_users --only pacientes

# Limpiar y recrear todo
python manage.py seed_users --clear
```

**Crea:**
- 6 médicos (5 médicos + 1 director)
- 5 pacientes de ejemplo
- 2 administrativos (admin + operador lab)

## 👥 Usuarios Creados

### 🩺 **Médicos** (password: `medico123`)
| Email | Nombre | DNI | Teléfono |
|-------|--------|-----|----------|
| dr.martinez@clinicaenvy.com | Dr. Roberto Martínez | 12345678 | 1154778899 |
| dra.lopez@clinicaenvy.com | Dra. María López | 23456789 | 1145889966 |
| dr.garcia@clinicaenvy.com | Dr. Carlos García | 34567890 | 1156990077 |
| dra.rodriguez@clinicaenvy.com | Dra. Ana Rodríguez | 45678901 | 1167001188 |
| dr.fernandez@clinicaenvy.com | Dr. Alejandro Fernández | 56789012 | 1178112299 |

### 🏥 **Director Médico** (password: `director123`)
| Email | Nombre | DNI | Teléfono |
|-------|--------|-----|----------|
| dr.director@clinicaenvy.com | Dr. Eduardo Villareal | 11223344 | 1134778855 |

### 🤱 **Pacientes** (password: `paciente123`)
| Email | Nombre | DNI | Edad Aprox. | Sexo |
|-------|--------|-----|-------------|------|
| maria.gonzalez@email.com | María González | 33444555 | 39 años | F |
| lucia.perez@email.com | Lucía Pérez | 44555666 | 34 años | F |
| juan.martinez@email.com | Juan Martínez | 55666777 | 36 años | M |
| sofia.ramirez@email.com | Sofía Ramírez | 66777888 | 32 años | F |
| gabriel.torres@email.com | Gabriel Torres | 77888999 | 37 años | M |

### 🏢 **Administrativos**
| Email | Nombre | Password | Rol |
|-------|--------|----------|-----|
| admin@clinicaenvy.com | Carmen Administradora | `admin123` | ADMIN |
| laboratorio@clinicaenvy.com | Técnico Laboratorio | `lab123` | OPERADOR_LABORATORIO |

## 🚀 Uso Recomendado

### Para desarrollo inicial:
```bash
# 1. Aplicar migraciones
python manage.py migrate

# 2. Poblar con todos los usuarios
python manage.py seed_users

# 3. Verificar creación de usuarios
python manage.py shell
```

### Para resetear datos:
```bash
# Limpiar y recrear usuarios
python manage.py seed_users --clear

# Solo recrear médicos
python manage.py seed_medicos --clear
```

## 🔍 Verificación

Después de ejecutar los seeds, puedes verificar que todo esté correcto:

```bash
# Ver usuarios creados
python manage.py shell
>>> from CustomUser.models import CustomUser
>>> CustomUser.objects.all().count()
>>> CustomUser.objects.filter(rol='MEDICO').count()
>>> CustomUser.objects.filter(rol='PACIENTE').count()
```

## 📝 Notas Importantes

- **Contraseñas:** Todas las contraseñas son simples para desarrollo. En producción usar contraseñas seguras.
- **DNIs:** Los DNIs son ficticios para testing.
- **Emails:** Usar emails reales en producción.
- **Validaciones:** Los datos cumplen con las validaciones del modelo CustomUser.
- **Transacciones:** Todos los seeds usan transacciones atómicas para consistencia.

## 🛠️ Personalización

Para modificar los datos, edita los archivos en `CustomUser/management/commands/`:
- `seed_medicos.py` - Solo médicos
- `seed_users.py` - Todos los usuarios

Puedes cambiar nombres, emails, DNIs, teléfonos, etc. según tus necesidades.