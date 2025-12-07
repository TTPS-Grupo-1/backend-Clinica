# 📊 Guía Completa: Data Warehouse - Clínica de Fertilidad

Esta guía contiene todos los pasos para crear y poblar el Data Warehouse (DW) en PostgreSQL, cargar datos desde SQLite (Django) y conectar Power BI para análisis.

---

## 📋 Prerrequisitos

1. **PostgreSQL instalado y corriendo**
   - Versión recomendada: 12 o superior
   - Usuario con permisos para crear bases de datos (por defecto: `postgres`)

2. **Python 3.8+** con las siguientes librerías:
   ```powershell
   pip install psycopg2-binary
   ```

3. **Acceso a la base de datos SQLite de Django**
   - Ruta: `../project/db.sqlite3`

4. **Power BI Desktop** (opcional, para visualización)

---

## 🗄️ PASO 1: Crear la Base de Datos PostgreSQL

### 1.1. Conectar a PostgreSQL (PowerShell)

Abre PowerShell y conecta a PostgreSQL como superusuario:

```powershell
# Opción A: usando psql desde PowerShell (si está en PATH)
psql -U postgres

# Opción B: si psql no está en PATH, usar ruta completa
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Cuando te pida la contraseña, ingresa la contraseña del usuario `postgres` (la que configuraste al instalar PostgreSQL).

### 1.2. Crear la base de datos

Ejecuta este comando en el prompt de PostgreSQL:

```sql
CREATE DATABASE clinica_datawarehouse
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Argentina.1252'
    LC_CTYPE = 'Spanish_Argentina.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
```

Verifica que se creó:

```sql
\l
```

Deberías ver `clinica_datawarehouse` en la lista.

Sal de psql:

```sql
\q
```

---

## 🏗️ PASO 2: Crear las Tablas del Data Warehouse

### 2.1. Crear las dimensiones

Ejecuta el script SQL desde PowerShell:

```powershell
# Navega a la carpeta datawarehouse
cd C:\Users\feliu\OneDrive\Desktop\Facultad\TTPS\Back\backend-Clinica\datawarehouse

# Ejecuta el script de creación de dimensiones
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_dimensions.sql
```

**¿Qué hace este script?**
- Crea 10 tablas de dimensión: `Dim_Tiempo`, `Dim_Medico`, `Dim_Paciente`, `Dim_Operador`, `Dim_Tecnica`, `Dim_Objetivo`, `Dim_Calidad`, `Dim_Estado_Embrion`, `Dim_Estado_Ovocito`, `Dim_Obra_Social`.

### 2.2. Poblar dimensiones básicas (catálogos)

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse -f populate_dimensions.sql
```

**¿Qué hace este script?**
- Inserta valores predefinidos en `Dim_Tecnica` (FIV, ICSI, IA)
- Inserta valores en `Dim_Calidad` (A, B, C, D)
- Inserta estados de embriones y ovocitos

### 2.3. Crear las tablas de hechos

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_facts.sql
```

**¿Qué hace este script?**
- Crea 8 tablas de hechos: `Fact_Tratamiento`, `Fact_Fertilizacion`, `Fact_Monitoreo`, `Fact_Embrion`, `Fact_Ovocito`, `Fact_Donacion_Semen`, `Fact_Pago`, `Fact_Paciente_Actividad`.
- Establece claves foráneas hacia las dimensiones.

### 2.4. Verificar que las tablas se crearon

Conecta a la base de datos:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse
```

Lista las tablas:

```sql
\dt
```

Deberías ver algo como:

```
             List of relations
 Schema |          Name          | Type  |  Owner   
--------+------------------------+-------+----------
 public | dim_calidad            | table | postgres
 public | dim_estado_embrion     | table | postgres
 public | dim_estado_ovocito     | table | postgres
 public | dim_medico             | table | postgres
 public | dim_obra_social        | table | postgres
 public | dim_objetivo           | table | postgres
 public | dim_operador           | table | postgres
 public | dim_paciente           | table | postgres
 public | dim_tecnica            | table | postgres
 public | dim_tiempo             | table | postgres
 public | fact_donacion_semen    | table | postgres
 public | fact_embrion           | table | postgres
 public | fact_fertilizacion     | table | postgres
 public | fact_monitoreo         | table | postgres
 public | fact_ovocito           | table | postgres
 public | fact_paciente_actividad| table | postgres
 public | fact_pago              | table | postgres
 public | fact_tratamiento       | table | postgres
```

Sal de psql:

```sql
\q
```

---

## 📦 PASO 3: Generar Datos de Prueba Masivos

Tienes **DOS OPCIONES** para poblar el Data Warehouse:

### **OPCIÓN A: Generar Datos de Prueba (Recomendado para Testing)** ⚡

Usa el script `generate_test_data.py` que genera datos sintéticos realistas directamente en PostgreSQL.

#### 3.1. Configurar credenciales

Abre `generate_test_data.py` y cambia la contraseña:

```python
PG_CONFIG = {
    'host': 'localhost',
    'database': 'clinica_datawarehouse',
    'user': 'postgres',
    'password': 'admin'  # ⚠️ CAMBIA ESTO por tu contraseña real
}
```

#### 3.2. Ejecutar el generador

```powershell
# Navega a la carpeta datawarehouse
cd C:\Users\feliu\OneDrive\Desktop\Facultad\TTPS\Back\backend-Clinica\datawarehouse

# Activa virtualenv
..\venv\Scripts\activate

# Ejecuta el generador
python generate_test_data.py
```

**¿Qué genera?**
- ✅ 4,018 fechas (2020-2030)
- ✅ 15 médicos (3 directores)
- ✅ 200 pacientes con datos realistas
- ✅ 8 operadores de laboratorio
- ✅ 350 tratamientos (70% activos, 30% finalizados)
- ✅ 180 fertilizaciones con tasas de éxito variables
- ✅ 600 embriones (diferentes estados y calidades)
- ✅ 800 ovocitos
- ✅ Datos de 6 objetivos y 8 obras sociales

**Ventajas:**
- 🚀 Rápido (1-2 minutos)
- 📊 Datos coherentes y realistas
- 🔄 Puedes ejecutarlo múltiples veces (limpia y regenera)
- 🧪 Perfecto para pruebas y demos

---

### **OPCIÓN B: ETL desde Django (Datos Reales)** 🔄

Si ya tienes datos en tu aplicación Django, usa el ETL para copiarlos.

#### 3.1. Configurar credenciales en `etl_script.py`

```python
PG_CONFIG = {
    'host': 'localhost',
    'database': 'clinica_datawarehouse',
    'user': 'postgres',
    'password': 'admin'  # ⚠️ CAMBIA ESTO
}
```

#### 3.2. Ejecutar el ETL

```powershell
cd C:\Users\feliu\OneDrive\Desktop\Facultad\TTPS\Back\backend-Clinica\datawarehouse
..\venv\Scripts\activate
python etl_script.py
```

---

### 3.3. Verificar que los datos se cargaron

Conecta a PostgreSQL:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse
```

Consulta algunos datos:

```sql
-- Contar registros en Fact_Tratamiento
SELECT COUNT(*) FROM fact_tratamiento;

-- Ver primeros 5 tratamientos con datos de paciente y médico
SELECT 
    t.tratamiento_id,
    p.nombre_completo AS paciente,
    m.nombre_completo AS medico,
    t.fecha_inicio,
    t.etapa_alcanzada,
    t.activo
FROM fact_tratamiento t
JOIN dim_paciente p ON t.paciente_key = p.paciente_id
JOIN dim_medico m ON t.medico_key = m.medico_id
LIMIT 5;

-- Contar embriones por calidad
SELECT 
    c.calidad,
    COUNT(*) as cantidad
FROM fact_embrion e
JOIN dim_calidad c ON e.calidad_key = c.calidad_id
GROUP BY c.calidad
ORDER BY c.calidad;
```

Sal de psql:

```sql
\q
```

---

## 📊 PASO 4: Conectar Power BI

### 4.1. Abrir Power BI Desktop

1. Abre Power BI Desktop
2. Click en **Obtener datos** → **Más...**
3. Busca **PostgreSQL database**
4. Click en **Conectar**

### 4.2. Configurar la conexión

En la ventana de conexión ingresa:

- **Servidor**: `localhost`
- **Base de datos**: `clinica_datawarehouse`
- Click en **Aceptar**

### 4.3. Autenticación

Selecciona:
- **Base de datos**
- **Nombre de usuario**: `postgres`
- **Contraseña**: tu contraseña de PostgreSQL
- Click en **Conectar**

### 4.4. Seleccionar tablas

En el navegador que aparece:
1. Marca las tablas que quieres importar (Fact_* y Dim_*)
2. Puedes hacer click en **Transformar datos** para ver/editar o **Cargar** directamente

### 4.5. Crear relaciones (si no se detectaron automáticamente)

En Power BI, ve a la vista de **Modelo** y crea las relaciones:

- `Fact_Tratamiento.paciente_key` → `Dim_Paciente.paciente_id`
- `Fact_Tratamiento.medico_key` → `Dim_Medico.medico_id`
- `Fact_Tratamiento.fecha_inicio_key` → `Dim_Tiempo.tiempo_id`
- `Fact_Fertilizacion.tratamiento_id` → `Fact_Tratamiento.tratamiento_id`
- etc.

---

## 🔄 PASO 5: Actualizar el Data Warehouse

Cuando haya nuevos datos en Django, vuelve a ejecutar el ETL:

```powershell
cd C:\Users\feliu\OneDrive\Desktop\Facultad\TTPS\Back\backend-Clinica\datawarehouse
..\venv\Scripts\activate
python etl_script.py
```

El ETL tiene lógica de `ON CONFLICT DO UPDATE` que actualiza registros existentes y agrega nuevos.

En Power BI, haz click en **Actualizar** para ver los datos nuevos.

---

## 📈 Consultas de Ejemplo (SQL)

### Tratamientos por médico y estado

```sql
SELECT 
    m.nombre_completo AS medico,
    t.activo,
    COUNT(*) AS total_tratamientos
FROM fact_tratamiento t
JOIN dim_medico m ON t.medico_key = m.medico_id
GROUP BY m.nombre_completo, t.activo
ORDER BY total_tratamientos DESC;
```

### Tasa de éxito por técnica de fertilización

```sql
SELECT 
    tec.nombre AS tecnica,
    COUNT(*) AS total_fertilizaciones,
    SUM(CASE WHEN f.exitosa THEN 1 ELSE 0 END) AS exitosas,
    ROUND(100.0 * SUM(CASE WHEN f.exitosa THEN 1 ELSE 0 END) / COUNT(*), 2) AS tasa_exito_pct
FROM fact_fertilizacion f
JOIN dim_tecnica tec ON f.tecnica_key = tec.tecnica_id
GROUP BY tec.nombre;
```

### Embriones generados por mes

```sql
SELECT 
    t.anio,
    t.mes,
    t.nombre_mes,
    COUNT(e.embrion_id) AS total_embriones
FROM fact_embrion e
JOIN dim_tiempo t ON e.fecha_key = t.tiempo_id
GROUP BY t.anio, t.mes, t.nombre_mes
ORDER BY t.anio, t.mes;
```

### Pacientes con tratamientos activos

```sql
SELECT 
    p.nombre_completo,
    p.dni,
    COUNT(t.tratamiento_id) AS tratamientos_activos
FROM fact_tratamiento t
JOIN dim_paciente p ON t.paciente_key = p.paciente_id
WHERE t.activo = TRUE
GROUP BY p.nombre_completo, p.dni
ORDER BY tratamientos_activos DESC;
```

---

## 🛠️ Troubleshooting

### Error: "psql: command not found"

Usa la ruta completa:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

O agrega PostgreSQL al PATH de Windows.

### Error: "password authentication failed"

Verifica la contraseña del usuario `postgres`. Si olvidaste la contraseña, puedes:
1. Editar `pg_hba.conf` (en `C:\Program Files\PostgreSQL\15\data\`)
2. Cambiar `md5` por `trust` temporalmente
3. Reiniciar el servicio PostgreSQL
4. Cambiar la contraseña con `ALTER USER postgres PASSWORD 'nueva_pass';`
5. Volver a poner `md5` en `pg_hba.conf`

### Error: "relation does not exist"

Las tablas no se crearon. Vuelve a ejecutar los scripts SQL:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_dimensions.sql
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_facts.sql
```

### Error en el ETL: "No module named 'psycopg2'"

Instala la librería:

```powershell
pip install psycopg2-binary
```

### Error: "no such table: Medicos_medico"

Verifica que la ruta al archivo SQLite sea correcta en `etl_script.py`:

```python
SQLITE_DB = '../project/db.sqlite3'
```

Ajusta la ruta relativa según tu estructura de carpetas.

---

## 📚 Recursos Adicionales

- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de Power BI](https://docs.microsoft.com/en-us/power-bi/)
- [Psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## ✅ Checklist de Implementación

- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos `clinica_datawarehouse` creada
- [ ] Scripts SQL ejecutados (dimensiones + hechos)
- [ ] Dimensiones básicas pobladas
- [ ] Credenciales configuradas en `etl_script.py`
- [ ] ETL ejecutado exitosamente
- [ ] Datos verificados en PostgreSQL
- [ ] Power BI conectado
- [ ] Relaciones configuradas en Power BI
- [ ] Primeros dashboards creados

---

**Última actualización**: Diciembre 2025  
**Autor**: Equipo TTPS Grupo 1
