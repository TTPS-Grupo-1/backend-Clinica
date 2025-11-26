# Casos de Prueba - Sistema de Fertilidad

Este documento describe todos los casos de prueba que el comando `init_db` crea automáticamente para facilitar el testing del sistema.

## 📋 Índice

1. [Usuarios Base](#usuarios-base)
2. [Casos de Prueba por Etapa de Tratamiento](#casos-de-prueba-por-etapa-de-tratamiento)
3. [Casos de Segunda Consulta](#casos-de-segunda-consulta)
4. [Casos de Monitoreo](#casos-de-monitoreo)
5. [Datos Complementarios](#datos-complementarios)
6. [Cómo Ejecutar](#cómo-ejecutar)

---

## 👥 Usuarios Base

### Médicos (Password: `12345678`)

| Email | Nombre | Rol | Notas |
|---|---|---|---|
| dr.garcia@clinica.com | Dr. Juan García | MEDICO | Médico principal |
| dra.lopez@clinica.com | Dra. María López | MEDICO | Médica principal |
| dr.martinez@clinica.com | Dr. Carlos Martínez | MEDICO | Médico principal |
| **extra.medico@clinica.com** | **Extra Medico** | **MEDICO** | **Médico para casos especiales** |

### Pacientes Base (Password: `12345678`)

| Email | Nombre | Rol | Tratamiento |
|---|---|---|---|
| ana.fernandez@email.com | Ana Fernández | PACIENTE | Con primera y segunda consulta |
| lucia.gomez@email.com | Lucía Gómez | PACIENTE | Con primera y segunda consulta |
| sofia.rodriguez@email.com | Sofía Rodríguez | PACIENTE | Con primera y segunda consulta |

### Operador de Laboratorio

| Email | Password | Rol |
|---|---|---|
| operador.lab@clinica.com | `labpass123` | OPERADOR_LABORATORIO |

---

## 🧪 Casos de Prueba por Etapa de Tratamiento

El sistema crea **4 pacientes extra** que representan diferentes estados del flujo de atención:

### 1️⃣ **Paciente sin Tratamiento (Primera Consulta Pendiente)**

**Usuario:** `extra.paciente@email.com` (Password: `12345678`)

- **Nombre:** Extra Paciente
- **Estado:** Sin tratamiento creado
- **Turno reservado:** ✅ Sí (con médico Extra Medico)
- **Próximo paso:** Primera Consulta

**Caso de uso:**
- Al hacer click en "Atender" desde el listado de turnos
- El sistema detecta que NO tiene tratamiento
- Redirige automáticamente a `/pacientes/{id}/primeraConsulta`

---

### 2️⃣ **Paciente con Primera Consulta Completada (Segunda Consulta Pendiente)**

**Usuario:** `paciente.pc@email.com` (Password: `12345678`)

- **Nombre:** Pedro Primera
- **Estado:** Primera consulta completada
- **Tratamiento:** ✅ Creado con primera consulta
- **Turno reservado:** ✅ Sí (para segunda consulta)
- **Próximo paso:** Segunda Consulta

**Caso de uso:**
- Al hacer click en "Atender"
- El sistema detecta que tiene primera consulta pero NO segunda
- Redirige a `/pacientes/{id}/segundaConsulta/{tratamientoId}`

---

### 3️⃣ **Paciente con Ambas Consultas Completadas (Monitoreo Pendiente)**

**Usuario:** `paciente.sc@email.com` (Password: `12345678`)

- **Nombre:** Sara Segunda
- **Estado:** Primera y segunda consulta completadas
- **Tratamiento:** ✅ Creado con ambas consultas
- **Turno reservado:** ✅ Sí (marcado como `es_monitoreo=True`)
- **Monitoreo:** ✅ 1 monitoreo pendiente asociado al turno
- **Próximo paso:** Atender Monitoreo

**Caso de uso:**
- Al hacer click en "Atender"
- El sistema detecta que tiene ambas consultas completadas
- El turno está marcado como `es_monitoreo=True`
- Busca el monitoreo más próximo y redirige a `/medico/monitoreos?monitoreoId={id}`

---

### 4️⃣ **Paciente con Múltiples Monitoreos**

**Usuario:** `paciente.mon@email.com` (Password: `12345678`)

- **Nombre:** Marta Monitoreo
- **Estado:** Primera y segunda consulta completadas
- **Tratamiento:** ✅ Creado con ambas consultas
- **Monitoreos:**
  - ✅ **Monitoreo 1:** Atendido (hace 10 días) - completado con descripción
  - 🕒 **Monitoreo 2:** Pendiente (mañana) - tiene turno reservado
  - 📅 **Monitoreo 3:** Futuro (en 7 días) - sin turno asignado

**Caso de uso:**
- Al hacer click en "Atender" el turno del Monitoreo 2
- El sistema detecta ambas consultas completadas
- Busca el monitoreo NO atendido más cercano a la fecha actual
- Redirige a `/medico/monitoreos?monitoreoId={monitoreo2_id}`
- Permite ver el historial de monitoreos previos

---

## 🔬 Casos de Segunda Consulta

Los 3 pacientes base tienen **diferentes escenarios de viabilidad de gametos**:

### Escenario 1: Semen y Ovocito Viables ✅✅
**Paciente:** Ana Fernández
- `semen_viable`: `true`
- `ovocito_viable`: `true`
- **Flujo:** Continúa normalmente con fertilización

### Escenario 2: Semen NO Viable, Ovocito Viable ❌✅
**Paciente:** Lucía Gómez
- `semen_viable`: `false`
- `ovocito_viable`: `true`
- **Flujo:** Debe usar Banco de Semen

### Escenario 3: Ninguno Viable ❌❌
**Paciente:** Sofía Rodríguez
- `semen_viable`: `false`
- `ovocito_viable`: `false`
- **Flujo:** Debe usar Banco de Semen Y Banco de Ovocitos

---

## 📊 Casos de Monitoreo

Cada paciente base tiene **3 monitoreos** con diferentes estados:

| Monitoreo | Estado | Fecha | Descripción |
|---|---|---|---|
| #1 | ✅ Atendido | Hace 7 días | "Paciente presenta evolución favorable..." |
| #2 | 🕒 Pendiente | Hoy (en 2 horas) | Sin descripción |
| #3 | 📅 Futuro | En 3 días | Sin descripción |

**URLs de prueba:**
```
http://localhost:5173/medico/monitoreos?monitoreoId=1
http://localhost:5173/medico/monitoreos?monitoreoId=2
http://localhost:5173/medico/monitoreos?monitoreoId=3
```

---

## 🧬 Datos Complementarios

### Punciones y Ovocitos

Cada paciente base tiene:
- **1 Punción** con fecha de hace 10-12 días
- **5 Ovocitos** por punción con diferentes estados:
  1. Ovocito **fresco**
  2. Ovocito **descartado**
  3. Ovocito **criopreservado**
  4. Ovocito **fertilizado**
  5. Ovocito **fresco** (segundo)

### Historial de Ovocitos

Los ovocitos tienen historial de cambios de estado según su tipo:
- **Frescos:** 1 evento (estado actual)
- **Criopreservados:** 2 eventos (fresco → criopreservado)
- **Fertilizados:** 2 eventos (fresco → fertilizado)

### Primera Consulta - Datos Completos

Cada paciente tiene:
- ✅ **Fenotipo:** color de ojos, pelo, tipo de pelo, altura, complexión, rasgos étnicos
- ✅ **Antecedentes Ginecológicos:** menarca, ciclo menstrual, G-P-Ab-St
- ✅ **Antecedentes Personales:** hábitos (tabaco, alcohol, drogas)
- ✅ **Resultados de Estudios:** FSH, LH, AMH, Espermiograma (4 estudios por paciente)

---

## 🎯 Objetivos de Tratamiento

Los tratamientos tienen diferentes objetivos para probar todos los casos:

1. **"Embarazo gameto propio"** - Pareja heterosexual
2. **"Embarazo con pareja del mismo sexo"** - Pareja lesbiana
3. **"Mujer sin pareja - Donante de espermatozoide"** - Mujer sola
4. **"ROPA - Una aporta la célula y la otra el óvulo"** - Técnica ROPA

---

## 🚀 Cómo Ejecutar

### Crear todos los datos de prueba

```bash
cd backend-Clinica/project
python manage.py init_db
```

### Limpiar y recrear todo

```bash
python manage.py init_db --clear
```

### Omitir creación de turnos en API (solo datos locales)

```bash
python manage.py init_db --skip-turnos
```

---

## 📝 Notas Importantes

### Turnos y API Externa

- Los turnos se crean **sincronizados** entre la base local y la API externa
- Cada turno local tiene un `id_externo` que corresponde al ID en la API
- Los turnos se reservan automáticamente para los pacientes correspondientes
- El médico "Extra Medico" tiene horarios específicos creados en la API

### Verificación de Turnos

Al ejecutar `init_db`, el sistema:
1. ✅ Elimina turnos existentes en la API
2. ✅ Crea horarios masivos para cada médico
3. ✅ Reserva turnos específicos para cada caso de prueba
4. ✅ Crea turnos locales con `id_externo` sincronizado
5. ✅ Verifica que el turno extra esté correctamente asignado en la API

### Variables de Entorno Requeridas

```bash
export TOKEN_GRUPO_3="tu_token_de_api_externa"
```

---

## 🔗 Flujos de Testing Recomendados

### 1. Testing de Primera Consulta
1. Login con `extra.medico@clinica.com`
2. Ir a "Listado de Turnos"
3. Click en "Atender" del paciente "Extra Paciente"
4. Completar primera consulta

### 2. Testing de Segunda Consulta
1. Login con `extra.medico@clinica.com`
2. Ir a "Listado de Turnos"
3. Click en "Atender" del paciente "Pedro Primera"
4. Completar segunda consulta

### 3. Testing de Monitoreo
1. Login con `extra.medico@clinica.com`
2. Ir a "Listado de Turnos"
3. Click en "Atender" del paciente "Sara Segunda"
4. Sistema redirige automáticamente al monitoreo pendiente
5. Completar monitoreo

### 4. Testing de Múltiples Monitoreos
1. Login con `extra.medico@clinica.com`
2. Ir a "Listado de Turnos"
3. Click en "Atender" del paciente "Marta Monitoreo"
4. Sistema muestra el monitoreo más próximo (Monitoreo 2)
5. Ver historial de monitoreos anteriores

---

## ✅ Checklist de Funcionalidades Probadas

- [x] Primera consulta desde turno sin tratamiento
- [x] Segunda consulta desde turno con primera completa
- [x] Monitoreo desde turno con ambas consultas
- [x] Búsqueda de monitoreo más próximo
- [x] Banco de semen (semen no viable)
- [x] Banco de ovocitos (ovocito no viable)
- [x] Múltiples estados de ovocitos
- [x] Historial de cambios de estado de ovocitos
- [x] Sincronización de turnos con API externa
- [x] Diferentes objetivos de tratamiento
- [x] Punciones y ovocitos asociados
- [x] Resultados de estudios completos

---

## 📞 Soporte

Si encuentras algún problema con los datos de prueba:
1. Ejecuta `python manage.py init_db --clear` para resetear todo
2. Verifica que la variable `TOKEN_GRUPO_3` esté configurada
3. Revisa los logs en la consola para ver qué datos se crearon

---

**Última actualización:** Noviembre 2025