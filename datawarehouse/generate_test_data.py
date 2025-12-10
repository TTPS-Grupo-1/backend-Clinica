"""
Script de Generación Masiva de Datos de Prueba
Data Warehouse - Clínica de Fertilidad

Genera datos sintéticos realistas directamente en PostgreSQL
sin depender de la base de datos SQLite de Django.
"""

import psycopg2
from datetime import datetime, timedelta
import random
from faker import Faker

# ====================================
# CONFIGURACIÓN
# ====================================
PG_CONFIG = {
    'host': 'localhost',
    'database': 'clinica_datawarehouse',
    'user': 'postgres',
    'password': 'admin'  # ⚠️ CAMBIA ESTO
}

# Cantidad de registros a generar
CANTIDAD = {
    'medicos': 3,
    'pacientes': 200,
    'operadores': 8,
    'tratamientos': 350,
    'fertilizaciones': 180,
    'embriones': 600,
    'ovocitos': 800,
    'monitoreos': 450,
}

# Inicializar Faker para datos realistas
fake = Faker('es_AR')  # Español Argentina
Faker.seed(12345)
random.seed(12345)

print("🧬 GENERADOR DE DATOS MASIVOS - Data Warehouse Clínica de Fertilidad")
print("=" * 70)

# ====================================
# CONEXIÓN
# ====================================
print("\n🔄 Conectando a PostgreSQL...")
try:
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    print("✅ Conectado a PostgreSQL\n")
except Exception as e:
    print(f"❌ Error conectando a PostgreSQL: {e}")
    print("💡 Verifica la contraseña en PG_CONFIG (línea 16)")
    exit(1)

# ====================================
# 1. POBLAR DIM_TIEMPO (2020-2030)
# ====================================
print("📅 [1/9] Poblando Dim_Tiempo (2020-2030)...")
start_date = datetime(2020, 1, 1)
end_date = datetime(2030, 12, 31)
current_date = start_date
tiempo_count = 0

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

DIAS_ES = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

while current_date <= end_date:
    pg_cursor.execute("""
        INSERT INTO Dim_Tiempo (fecha, dia, mes, trimestre, anio, nombre_mes, nombre_dia_semana, es_fin_semana)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (fecha) DO NOTHING
    """, (
        current_date.date(),
        current_date.day,
        current_date.month,
        (current_date.month - 1) // 3 + 1,
        current_date.year,
        MESES_ES[current_date.month],
        DIAS_ES[current_date.weekday()],
        current_date.weekday() in [5, 6]
    ))
    current_date += timedelta(days=1)
    tiempo_count += 1

pg_conn.commit()
print(f"✅ {tiempo_count} fechas insertadas\n")

# ====================================
# 2. POBLAR DIM_MEDICO
# ====================================
print(f"👨‍⚕️ [2/9] Generando {CANTIDAD['medicos']} médicos...")
medicos_ids = []
especialidades = ['Fertilidad', 'Ginecología', 'Endocrinología Reproductiva', 'Andrología']

for i in range(1, CANTIDAD['medicos'] + 1):
    dni = random.randint(20000000, 45000000)
    nombre = fake.first_name()
    apellido = fake.last_name()
    email = f"{nombre.lower()}.{apellido.lower()}@clinica.com.ar"
    is_director = i == 1  # Solo el primero es director
    
    pg_cursor.execute("""
        INSERT INTO Dim_Medico (medico_id, dni, nombre_completo, email, activo, eliminado, is_director)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (medico_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo,
            email = EXCLUDED.email
    """, (i, dni, f"Dr. {nombre} {apellido}", email, True, False, is_director))
    
    medicos_ids.append(i)

pg_conn.commit()
print(f"✅ {len(medicos_ids)} médicos insertados\n")

# ====================================
# 3. POBLAR DIM_PACIENTE
# ====================================
print(f"🧑‍🦱 [3/9] Generando {CANTIDAD['pacientes']} pacientes...")
pacientes_ids = []
obras_sociales = ['OSDE', 'Swiss Medical', 'Galeno', 'IOMA', 'PAMI', 'Particular', 'Medicus', 'Sancor Salud']
sexos = ['Femenino', 'Masculino']

for i in range(1, CANTIDAD['pacientes'] + 1):
    dni = random.randint(25000000, 45000000)
    nombre = fake.first_name()
    apellido = fake.last_name()
    edad = random.randint(25, 45)
    sexo = random.choice(sexos)
    obra_social = random.choice(obras_sociales)
    
    pg_cursor.execute("""
        INSERT INTO Dim_Paciente (paciente_id, dni, nombre_completo, edad, sexo, obra_social, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (paciente_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo,
            edad = EXCLUDED.edad
    """, (i, dni, f"{nombre} {apellido}", edad, sexo, obra_social, True))
    
    pacientes_ids.append(i)
    
    # Insertar obra social en Dim_Obra_Social
    pg_cursor.execute("""
        INSERT INTO Dim_Obra_Social (nombre) VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
    """, (obra_social,))

pg_conn.commit()
print(f"✅ {len(pacientes_ids)} pacientes insertados\n")

# ====================================
# 4. POBLAR DIM_OPERADOR
# ====================================
print(f"🔬 [4/9] Generando {CANTIDAD['operadores']} operadores de laboratorio...")
operadores_ids = []

for i in range(1, CANTIDAD['operadores'] + 1):
    nombre = fake.first_name()
    apellido = fake.last_name()
    email = f"{nombre.lower()}.{apellido.lower()}.lab@clinica.com.ar"
    
    pg_cursor.execute("""
        INSERT INTO Dim_Operador (operador_id, nombre_completo, email)
        VALUES (%s, %s, %s)
        ON CONFLICT (operador_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo
    """, (i, f"{nombre} {apellido}", email))
    
    operadores_ids.append(i)

pg_conn.commit()
print(f"✅ {len(operadores_ids)} operadores insertados\n")

# ====================================
# 5. POBLAR DIM_OBJETIVO
# ====================================
print("🎯 [5/9] Poblando Dim_Objetivo...")
objetivos = [
    'Pareja hombre y mujer',
    'Pareja de dos femeninas',
    'Pareja de dos femeninas (Metodo Ropa)',
    'Mujer sin pareja'
]

for obj in objetivos:
    pg_cursor.execute("""
        INSERT INTO Dim_Objetivo (nombre) VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
    """, (obj,))

pg_conn.commit()
print(f"✅ {len(objetivos)} objetivos insertados\n")

# ====================================
# HELPER: Obtener tiempo_id
# ====================================
def get_tiempo_id(fecha):
    """Obtiene el tiempo_id de una fecha"""
    pg_cursor.execute("SELECT tiempo_id FROM Dim_Tiempo WHERE fecha = %s", (fecha,))
    result = pg_cursor.fetchone()
    return result[0] if result else None

# ====================================
# 6. POBLAR FACT_TRATAMIENTO
# ====================================
print(f"💊 [6/9] Generando {CANTIDAD['tratamientos']} tratamientos...")
tratamientos_ids = []
etapas_posibles = ['Primera Consulta', 'Segunda Consulta', 'Monitoreo','Punción', 'Fertilización', 'Transferencia','Seguimiento', 'Finalizado']
motivos_fin = ['Nacido vivo', 'Nacido no vivo', 'Tratamiento cancelado'] # esto acomodarlo

for i in range(1, CANTIDAD['tratamientos'] + 1):
    paciente_id = random.choice(pacientes_ids)
    medico_id = random.choice(medicos_ids)
    objetivo = random.choice(objetivos)
    
    # Fecha de inicio entre 2022 y 2024
    fecha_inicio = fake.date_between(start_date=datetime(2022, 1, 1), end_date=datetime(2024, 11, 30))
    
    # 70% activos, 30% finalizados
    activo = random.random() < 0.7
    
    if activo:
        fecha_fin = None
        motivo_fin = None
        exitoso = None
        duracion = None
    else:
        duracion = random.randint(30, 180)
        fecha_fin = fecha_inicio + timedelta(days=duracion)
        motivo_fin = random.choice(motivos_fin)
        exitoso = motivo_fin == 'Embarazo logrado' if motivo_fin else None
    
    # Determinar etapas completadas
    etapa_alcanzada = random.choice(etapas_posibles)
    etapas_idx = etapas_posibles.index(etapa_alcanzada)
    
    primera_ok = etapas_idx >= 0
    segunda_ok = etapas_idx >= 1
    puncion_ok = etapas_idx >= 2
    fert_ok = etapas_idx >= 3
    trans_ok = etapas_idx >= 4
    
    fecha_inicio_key = get_tiempo_id(fecha_inicio)
    fecha_fin_key = get_tiempo_id(fecha_fin) if fecha_fin else None
    
    # Obtener objetivo_key
    pg_cursor.execute("SELECT objetivo_id FROM Dim_Objetivo WHERE nombre = %s", (objetivo,))
    objetivo_key = pg_cursor.fetchone()[0]
    
    pg_cursor.execute("""
        INSERT INTO Fact_Tratamiento (
            tratamiento_id, paciente_id, medico_id, fecha_inicio, fecha_finalizacion,
            objetivo, activo, motivo_finalizacion, exitoso, etapa_alcanzada, duracion_dias,
            primera_consulta_completada, segunda_consulta_completada,
            puncion_realizada, fertilizacion_realizada, transferencia_realizada,
            fecha_inicio_key, fecha_fin_key, medico_key, paciente_key, objetivo_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tratamiento_id) DO NOTHING
    """, (
        i, paciente_id, medico_id, fecha_inicio, fecha_fin,
        objetivo, activo, motivo_fin, exitoso, etapa_alcanzada, duracion,
        primera_ok, segunda_ok, puncion_ok, fert_ok, trans_ok,
        fecha_inicio_key, fecha_fin_key, medico_id, paciente_id, objetivo_key
    ))
    
    tratamientos_ids.append({
        'id': i,
        'fecha_inicio': fecha_inicio,
        'fert_ok': fert_ok,
        'trans_ok': trans_ok
    })

pg_conn.commit()
print(f"✅ {len(tratamientos_ids)} tratamientos insertados\n")

# ====================================
# 7. POBLAR FACT_FERTILIZACION
# ====================================
print(f"🧬 [7/9] Generando {CANTIDAD['fertilizaciones']} fertilizaciones...")
fertilizaciones_ids = []
tecnicas = ['FIV', 'ICSI']
resultados = ['Exitosa', 'No exitosa']

# Obtener IDs de técnicas
tecnica_ids = {}
for tec in tecnicas:
    pg_cursor.execute("SELECT tecnica_id FROM Dim_Tecnica WHERE nombre = %s", (tec,))
    result = pg_cursor.fetchone()
    if result:
        tecnica_ids[tec] = result[0]

# Solo fertilizaciones de tratamientos que llegaron a esa etapa
tratamientos_con_fert = [t for t in tratamientos_ids if t['fert_ok']]
tratamientos_seleccionados = random.sample(tratamientos_con_fert, min(CANTIDAD['fertilizaciones'], len(tratamientos_con_fert)))

for i, trat in enumerate(tratamientos_seleccionados, 1):
    tratamiento_id = trat['id']
    operador_id = random.choice(operadores_ids)
    tecnica = random.choice(tecnicas)
    resultado = random.choice(resultados)
    
    # Fecha 20-40 días después del inicio del tratamiento
    fecha_fert = trat['fecha_inicio'] + timedelta(days=random.randint(20, 40))
    
    ovocitos_usados = random.randint(5, 15)
    embriones_gen = random.randint(2, min(ovocitos_usados, 10)) if resultado == 'Exitosa' else random.randint(0, 3)
    
    tasa_fert = round((embriones_gen / ovocitos_usados * 100), 2) if ovocitos_usados > 0 else 0
    exitosa = resultado == 'Exitosa'
    
    fecha_key = get_tiempo_id(fecha_fert)
    tecnica_key = tecnica_ids.get(tecnica)
    
    pg_cursor.execute("""
        INSERT INTO Fact_Fertilizacion (
            fertilizacion_id, tratamiento_id, operador_id, fecha_fertilizacion,
            tecnica, resultado, ovocitos_utilizados, embriones_generados, tasa_fertilizacion, exitosa,
            fecha_key, operador_key, tecnica_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (fertilizacion_id) DO NOTHING
    """, (
        i, tratamiento_id, operador_id, fecha_fert,
        tecnica, resultado, ovocitos_usados, embriones_gen, tasa_fert, exitosa,
        fecha_key, operador_id, tecnica_key
    ))
    
    fertilizaciones_ids.append({
        'id': i,
        'fecha': fecha_fert,
        'embriones': embriones_gen
    })

pg_conn.commit()
print(f"✅ {len(fertilizaciones_ids)} fertilizaciones insertadas\n")

# ====================================
# 8. POBLAR FACT_EMBRION
# ====================================
print(f"🔬 [8/9] Generando {CANTIDAD['embriones']} embriones...")
estados_embrion = ['fresco', 'criopreservado', 'transferido', 'descartado']
calidades = ['1', '2', '3', '4', '5']
resultados_pgt = ['Exitoso', 'No exitoso']

# Obtener IDs de estados y calidades
estado_ids = {}
for estado in estados_embrion:
    pg_cursor.execute("SELECT estado_id FROM Dim_Estado_Embrion WHERE estado = %s", (estado,))
    result = pg_cursor.fetchone()
    if result:
        estado_ids[estado] = result[0]

calidad_ids = {}
for cal in calidades:
    pg_cursor.execute("SELECT calidad_id FROM Dim_Calidad WHERE calidad = %s", (cal,))
    result = pg_cursor.fetchone()
    if result:
        calidad_ids[cal] = result[0]

embrion_id = 1
for fert in fertilizaciones_ids:
    num_embriones = min(fert['embriones'], random.randint(1, 8))
    
    for j in range(num_embriones):
        if embrion_id > CANTIDAD['embriones']:
            break
            
        estado = random.choice(estados_embrion)
        calidad = random.choice(calidades)
        
        # 30% tienen PGT
        pgt_realizado = random.random() < 0.3
        resultado_pgt = random.choice(resultados_pgt) if pgt_realizado else None
        
        fecha_creacion = fert['fecha'] + timedelta(days=random.randint(1, 5))
        fecha_key = get_tiempo_id(fecha_creacion)
        
        pg_cursor.execute("""
            INSERT INTO Fact_Embrion (
                embrion_id, fertilizacion_id, fecha_creacion, estado_actual, calidad,
                pgt_realizado, resultado_pgt, fecha_key, calidad_key, estado_key
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (embrion_id) DO NOTHING
        """, (
            embrion_id, fert['id'], fecha_creacion, estado, calidad,
            pgt_realizado, resultado_pgt, fecha_key, calidad_ids.get(calidad), estado_ids.get(estado)
        ))
        
        embrion_id += 1

pg_conn.commit()
print(f"✅ {embrion_id - 1} embriones insertados\n")

# ====================================
# 9. POBLAR FACT_OVOCITO
# ====================================
print(f"🥚 [9/9] Generando {CANTIDAD['ovocitos']} ovocitos...")
estados_ovocito = ['fresco', 'criopreservado', 'transferido', 'descartado']

# Obtener IDs de estados
estado_ovo_ids = {}
for estado in estados_ovocito:
    pg_cursor.execute("SELECT estado_id FROM Dim_Estado_Ovocito WHERE estado = %s", (estado,))
    result = pg_cursor.fetchone()
    if result:
        estado_ovo_ids[estado] = result[0]

for i in range(1, CANTIDAD['ovocitos'] + 1):
    # Asociar a una fertilización aleatoria (punción)
    fert = random.choice(fertilizaciones_ids)
    puncion_id = fert['id']  # Asumimos que puncion_id = fertilizacion_id para simplificar
    
    fecha_extraccion = fert['fecha'] - timedelta(days=random.randint(1, 3))
    estado = random.choice(estados_ovocito)
    calidad = random.choice(calidades)
    donado = random.random() < 0.05  # 5% donados
    
    fecha_key = get_tiempo_id(fecha_extraccion)
    
    pg_cursor.execute("""
        INSERT INTO Fact_Ovocito (
            ovocito_id, puncion_id, fecha_extraccion, estado_actual, calidad, donado,
            fecha_key, estado_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ovocito_id) DO NOTHING
    """, (
        i, puncion_id, fecha_extraccion, estado, calidad, donado,
        fecha_key, estado_ovo_ids.get(estado)
    ))

pg_conn.commit()
print(f"✅ {CANTIDAD['ovocitos']} ovocitos insertados\n")

# ====================================
# RESUMEN FINAL
# ====================================
print("\n" + "=" * 70)
print("🎉 GENERACIÓN DE DATOS COMPLETADA")
print("=" * 70)

# Contar registros en cada tabla
tablas = [
    ('Dim_Tiempo', 'dim_tiempo'),
    ('Dim_Medico', 'dim_medico'),
    ('Dim_Paciente', 'dim_paciente'),
    ('Dim_Operador', 'dim_operador'),
    ('Dim_Objetivo', 'dim_objetivo'),
    ('Dim_Obra_Social', 'dim_obra_social'),
    ('Fact_Tratamiento', 'fact_tratamiento'),
    ('Fact_Fertilizacion', 'fact_fertilizacion'),
    ('Fact_Embrion', 'fact_embrion'),
    ('Fact_Ovocito', 'fact_ovocito'),
]

print("\n📊 RESUMEN DE DATOS GENERADOS:")
print("-" * 70)
for nombre, tabla in tablas:
    pg_cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    count = pg_cursor.fetchone()[0]
    print(f"   {nombre:25} {count:>8} registros")

print("\n" + "=" * 70)
print("✅ Data Warehouse listo para análisis")
print("\n📝 PRÓXIMOS PASOS:")
print("   1. Conecta Power BI a: localhost / clinica_datawarehouse")
print("   2. Importa las tablas Dim_* y Fact_*")
print("   3. Crea relaciones en el modelo de datos")
print("   4. Diseña tus dashboards y reportes")
print("\n💡 Ejemplos de consultas en el README.md")
print("=" * 70)

# Cerrar conexión
pg_cursor.close()
pg_conn.close()
