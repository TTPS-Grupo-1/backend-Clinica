import sqlite3
import psycopg2
from datetime import datetime, timedelta

# ====================================
# CONFIGURACIÓN
# ====================================
SQLITE_DB = '../project/db.sqlite3'
PG_CONFIG = {
    'host': 'localhost',
    'database': 'clinica_datawarehouse',
    'user': 'postgres',
    'password': 'admin'  # ⚠️ CAMBIA ESTO
}

# ====================================
# CONEXIONES
# ====================================
print("🔄 Conectando a bases de datos...")
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
pg_conn = psycopg2.connect(**PG_CONFIG)
pg_cursor = pg_conn.cursor()
print("✅ Conectado a SQLite y PostgreSQL\n")

# ====================================
# FUNCIONES AUXILIARES
# ====================================
def get_tiempo_id(fecha_str):
    """Obtiene el tiempo_id de Dim_Tiempo para una fecha dada."""
    if not fecha_str:
        return None
    try:
        pg_cursor.execute("SELECT tiempo_id FROM Dim_Tiempo WHERE fecha = %s", (fecha_str,))
        result = pg_cursor.fetchone()
        return result[0] if result else None
    except:
        return None

# ====================================
# 1. POBLAR DIM_TIEMPO
# ====================================
print("📅 Poblando Dim_Tiempo...")
start_date = datetime(2020, 1, 1)
end_date = datetime(2030, 12, 31)
current_date = start_date

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
        current_date.year,  # ✅ Esto se guarda en "anio"
        current_date.strftime('%B'),
        current_date.strftime('%A'),
        current_date.weekday() in [5, 6]
    ))
    current_date += timedelta(days=1)

pg_conn.commit()
print("✅ Dim_Tiempo poblada\n")

# ====================================
# 2. POBLAR DIM_MEDICO
# ====================================
print("👨‍⚕️ Poblando Dim_Medico...")
medicos = sqlite_conn.execute("""
    SELECT id, dni, first_name, last_name, email, is_active, eliminado, is_director
    FROM Medicos_medico
""").fetchall()

for m in medicos:
    pg_cursor.execute("""
        INSERT INTO Dim_Medico (medico_id, dni, nombre_completo, email, activo, eliminado, is_director)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (medico_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo,
            email = EXCLUDED.email,
            activo = EXCLUDED.activo,
            eliminado = EXCLUDED.eliminado,
            is_director = EXCLUDED.is_director
    """, (
        m['id'],
        m['dni'],
        f"{m['first_name']} {m['last_name']}",
        m['email'],
        m['is_active'],
        m['eliminado'],
        m['is_director']
    ))

pg_conn.commit()
print(f"✅ {len(medicos)} médicos insertados\n")

# ====================================
# 3. POBLAR DIM_PACIENTE
# ====================================
print("🧑‍🦱 Poblando Dim_Paciente...")
pacientes = sqlite_conn.execute("""
    SELECT id, dni, first_name, last_name, edad, sexo, obra_social, is_active, created_at
    FROM Paciente_paciente
""").fetchall()

for p in pacientes:
    pg_cursor.execute("""
        INSERT INTO Dim_Paciente (paciente_id, dni, nombre_completo, edad, sexo, obra_social, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (paciente_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo,
            edad = EXCLUDED.edad,
            sexo = EXCLUDED.sexo,
            obra_social = EXCLUDED.obra_social,
            activo = EXCLUDED.activo
    """, (
        p['id'],
        p['dni'],
        f"{p['first_name']} {p['last_name']}",
        p['edad'],
        p['sexo'],
        p['obra_social'],
        p['is_active']
    ))
    
    # Poblar Dim_Obra_Social
    if p['obra_social']:
        pg_cursor.execute("""
            INSERT INTO Dim_Obra_Social (nombre)
            VALUES (%s)
            ON CONFLICT (nombre) DO NOTHING
        """, (p['obra_social'],))
    
    # Poblar Fact_Paciente_Actividad (Alta)
    if p['created_at']:
        fecha_alta = p['created_at'].split(' ')[0]  # Extraer solo fecha
        fecha_key = get_tiempo_id(fecha_alta)
        if fecha_key:
            pg_cursor.execute("""
                INSERT INTO Fact_Paciente_Actividad (paciente_id, fecha_evento, tipo_evento, fecha_key, paciente_key)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (p['id'], fecha_alta, 'Alta', fecha_key, p['id']))

pg_conn.commit()
print(f"✅ {len(pacientes)} pacientes insertados\n")

# ====================================
# 4. POBLAR DIM_OPERADOR
# ====================================
print("🔬 Poblando Dim_Operador...")
# Asumiendo que los operadores están en CustomUser con un rol específico
operadores = sqlite_conn.execute("""
    SELECT id, first_name, last_name, email
    FROM CustomUser_customuser
    WHERE rol = 'OPERADOR'
""").fetchall()

for op in operadores:
    pg_cursor.execute("""
        INSERT INTO Dim_Operador (operador_id, nombre_completo, email)
        VALUES (%s, %s, %s)
        ON CONFLICT (operador_id) DO UPDATE SET
            nombre_completo = EXCLUDED.nombre_completo,
            email = EXCLUDED.email
    """, (
        op['id'],
        f"{op['first_name']} {op['last_name']}",
        op['email']
    ))

pg_conn.commit()
print(f"✅ {len(operadores)} operadores insertados\n")

# ====================================
# 5. POBLAR DIM_OBJETIVO
# ====================================
print("🎯 Poblando Dim_Objetivo...")
objetivos = sqlite_conn.execute("""
    SELECT DISTINCT objetivo FROM Tratamiento_tratamiento WHERE objetivo IS NOT NULL
""").fetchall()

for obj in objetivos:
    pg_cursor.execute("""
        INSERT INTO Dim_Objetivo (nombre)
        VALUES (%s)
        ON CONFLICT (nombre) DO NOTHING
    """, (obj['objetivo'],))

pg_conn.commit()
print(f"✅ {len(objetivos)} objetivos insertados\n")

# ====================================
# 6. POBLAR FACT_TRATAMIENTO
# ====================================
print("💊 Poblando Fact_Tratamiento...")
tratamientos = sqlite_conn.execute("""
    SELECT 
        id, paciente_id, medico_id, fecha_inicio, activo, objetivo, 
        motivo_finalizacion, primera_consulta_id, segunda_consulta, 
        created_at, updated_at
    FROM Tratamiento_tratamiento
""").fetchall()

for t in tratamientos:
    # Determinar etapa alcanzada
    etapa = 'Sin Consulta'
    primera_ok = t['primera_consulta_id'] is not None
    segunda_ok = t['segunda_consulta']
    
    if primera_ok:
        etapa = 'Primera Consulta'
    if segunda_ok:
        etapa = 'Segunda Consulta'
    
    # Verificar punción
    puncion = sqlite_conn.execute(
        "SELECT COUNT(*) as cnt FROM Puncion_puncion WHERE tratamiento_id = ?",
        (t['id'],)
    ).fetchone()
    if puncion['cnt'] > 0:
        etapa = 'Punción'
    
    # Verificar fertilización
    fert = sqlite_conn.execute(
        "SELECT COUNT(*) as cnt FROM Fertilizacion_fertilizacion WHERE tratamiento_id = ?",
        (t['id'],)
    ).fetchone()
    if fert['cnt'] > 0:
        etapa = 'Fertilización'
    
    # Verificar transferencia
    trans = sqlite_conn.execute(
        "SELECT COUNT(*) as cnt FROM Transferencia_transferencia WHERE tratamiento_id = ?",
        (t['id'],)
    ).fetchone()
    if trans['cnt'] > 0:
        etapa = 'Transferencia'
    
    # Determinar si fue exitoso
    exitoso = None
    if t['motivo_finalizacion']:
        exitoso = 'embarazo' in t['motivo_finalizacion'].lower() or 'exitoso' in t['motivo_finalizacion'].lower()
    
    # Calcular duración
    duracion = None
    if not t['activo'] and t['updated_at']:
        try:
            inicio = datetime.strptime(t['fecha_inicio'], '%Y-%m-%d')
            fin = datetime.strptime(t['updated_at'].split(' ')[0], '%Y-%m-%d')
            duracion = (fin - inicio).days
        except:
            pass
    
    # Obtener claves
    fecha_inicio_key = get_tiempo_id(t['fecha_inicio'])
    fecha_fin_key = get_tiempo_id(t['updated_at'].split(' ')[0] if t['updated_at'] else None) if not t['activo'] else None
    
    objetivo_key = None
    if t['objetivo']:
        pg_cursor.execute("SELECT objetivo_id FROM Dim_Objetivo WHERE nombre = %s", (t['objetivo'],))
        res = pg_cursor.fetchone()
        objetivo_key = res[0] if res else None
    
    pg_cursor.execute("""
        INSERT INTO Fact_Tratamiento (
            tratamiento_id, paciente_id, medico_id, fecha_inicio, fecha_finalizacion,
            objetivo, activo, motivo_finalizacion, exitoso, etapa_alcanzada, duracion_dias,
            primera_consulta_completada, segunda_consulta_completada,
            puncion_realizada, fertilizacion_realizada, transferencia_realizada,
            fecha_inicio_key, fecha_fin_key, medico_key, paciente_key, objetivo_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tratamiento_id) DO UPDATE SET
            fecha_finalizacion = EXCLUDED.fecha_finalizacion,
            activo = EXCLUDED.activo,
            motivo_finalizacion = EXCLUDED.motivo_finalizacion,
            exitoso = EXCLUDED.exitoso,
            etapa_alcanzada = EXCLUDED.etapa_alcanzada,
            duracion_dias = EXCLUDED.duracion_dias,
            segunda_consulta_completada = EXCLUDED.segunda_consulta_completada,
            puncion_realizada = EXCLUDED.puncion_realizada,
            fertilizacion_realizada = EXCLUDED.fertilizacion_realizada,
            transferencia_realizada = EXCLUDED.transferencia_realizada
    """, (
        t['id'], t['paciente_id'], t['medico_id'], t['fecha_inicio'],
        t['updated_at'].split(' ')[0] if (not t['activo'] and t['updated_at']) else None,
        t['objetivo'], t['activo'], t['motivo_finalizacion'], exitoso, etapa, duracion,
        primera_ok, segunda_ok, puncion['cnt'] > 0, fert['cnt'] > 0, trans['cnt'] > 0,
        fecha_inicio_key, fecha_fin_key, t['medico_id'], t['paciente_id'], objetivo_key
    ))

pg_conn.commit()
print(f"✅ {len(tratamientos)} tratamientos insertados\n")

# ====================================
# 7. POBLAR FACT_FERTILIZACION
# ====================================
print("🧬 Poblando Fact_Fertilizacion...")
fertilizaciones = sqlite_conn.execute("""
    SELECT id, tratamiento_id, current_user_id, tecnica, resultado, created_at
    FROM Fertilizacion_fertilizacion
""").fetchall()

for f in fertilizaciones:
    # Contar embriones generados
    embriones_cnt = sqlite_conn.execute(
        "SELECT COUNT(*) as cnt FROM Embrion_embrion WHERE fertilizacion_id = ?",
        (f['id'],)
    ).fetchone()['cnt']
    
    # Determinar si fue exitosa
    exitosa = f['resultado'] and ('exitosa' in f['resultado'].lower() or 'exitoso' in f['resultado'].lower())
    
    # Obtener claves
    fecha_key = get_tiempo_id(f['created_at'].split(' ')[0] if f['created_at'] else None)
    
    tecnica_key = None
    if f['tecnica']:
        pg_cursor.execute("SELECT tecnica_id FROM Dim_Tecnica WHERE nombre = %s", (f['tecnica'],))
        res = pg_cursor.fetchone()
        tecnica_key = res[0] if res else None
    
    pg_cursor.execute("""
        INSERT INTO Fact_Fertilizacion (
            fertilizacion_id, tratamiento_id, operador_id, fecha_fertilizacion,
            tecnica, resultado, embriones_generados, exitosa,
            fecha_key, operador_key, tecnica_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (fertilizacion_id) DO UPDATE SET
            resultado = EXCLUDED.resultado,
            embriones_generados = EXCLUDED.embriones_generados,
            exitosa = EXCLUDED.exitosa
    """, (
        f['id'], f['tratamiento_id'], f['current_user_id'],
        f['created_at'].split(' ')[0] if f['created_at'] else None,
        f['tecnica'], f['resultado'], embriones_cnt, exitosa,
        fecha_key, f['current_user_id'], tecnica_key
    ))

pg_conn.commit()
print(f"✅ {len(fertilizaciones)} fertilizaciones insertadas\n")

# ====================================
# 8. POBLAR FACT_MONITOREO
# ====================================
print("📊 Poblando Fact_Monitoreo...")
monitoreos = sqlite_conn.execute("""
    SELECT id, tratamiento_id, created_at
    FROM Monitoreo_monitoreo
    ORDER BY tratamiento_id, created_at
""").fetchall()

# Contar monitoreos por tratamiento
tratamiento_contador = {}
for m in monitoreos:
    trat_id = m['tratamiento_id']
    if trat_id not in tratamiento_contador:
        tratamiento_contador[trat_id] = 0
    tratamiento_contador[trat_id] += 1
    
    fecha_key = get_tiempo_id(m['created_at'].split(' ')[0] if m['created_at'] else None)
    
    pg_cursor.execute("""
        INSERT INTO Fact_Monitoreo (tratamiento_id, fecha_monitoreo, numero_monitoreo, fecha_key, tratamiento_key)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (
        m['tratamiento_id'],
        m['created_at'].split(' ')[0] if m['created_at'] else None,
        tratamiento_contador[trat_id],
        fecha_key,
        m['tratamiento_id']
    ))

pg_conn.commit()
print(f"✅ {len(monitoreos)} monitoreos insertados\n")

# ====================================
# 9. POBLAR FACT_EMBRION
# ====================================
print("🔬 Poblando Fact_Embrion...")
embriones = sqlite_conn.execute("""
    SELECT id, fertilizacion_id, estado, calidad, pgt, created_at
    FROM Embrion_embrion
""").fetchall()

for e in embriones:
    fecha_key = get_tiempo_id(e['created_at'].split(' ')[0] if e['created_at'] else None)
    
    calidad_key = None
    if e['calidad']:
        pg_cursor.execute("SELECT calidad_id FROM Dim_Calidad WHERE calidad = %s", (e['calidad'],))
        res = pg_cursor.fetchone()
        calidad_key = res[0] if res else None
    
    estado_key = None
    if e['estado']:
        pg_cursor.execute("SELECT estado_id FROM Dim_Estado_Embrion WHERE estado = %s", (e['estado'].lower(),))
        res = pg_cursor.fetchone()
        estado_key = res[0] if res else None
    
    pg_cursor.execute("""
        INSERT INTO Fact_Embrion (
            embrion_id, fertilizacion_id, fecha_creacion, estado_actual, calidad,
            pgt_realizado, resultado_pgt, fecha_key, calidad_key, estado_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (embrion_id) DO UPDATE SET
            estado_actual = EXCLUDED.estado_actual,
            calidad = EXCLUDED.calidad,
            pgt_realizado = EXCLUDED.pgt_realizado,
            resultado_pgt = EXCLUDED.resultado_pgt
    """, (
        e['id'], e['fertilizacion_id'],
        e['created_at'].split(' ')[0] if e['created_at'] else None,
        e['estado'].lower() if e['estado'] else None,
        e['calidad'],
        e['pgt'] is not None,
        e['pgt'],
        fecha_key, calidad_key, estado_key
    ))

pg_conn.commit()
print(f"✅ {len(embriones)} embriones insertados\n")

# ====================================
# 10. POBLAR FACT_OVOCITO
# ====================================
print("🥚 Poblando Fact_Ovocito...")
ovocitos = sqlite_conn.execute("""
    SELECT id, puncion_id, estado, calidad, donado, created_at
    FROM Ovocito_ovocito
""").fetchall()

for o in ovocitos:
    fecha_key = get_tiempo_id(o['created_at'].split(' ')[0] if o['created_at'] else None)
    
    estado_key = None
    if o['estado']:
        pg_cursor.execute("SELECT estado_id FROM Dim_Estado_Ovocito WHERE estado = %s", (o['estado'].lower(),))
        res = pg_cursor.fetchone()
        estado_key = res[0] if res else None
    
    pg_cursor.execute("""
        INSERT INTO Fact_Ovocito (
            ovocito_id, puncion_id, fecha_extraccion, estado_actual, calidad, donado, fecha_key, estado_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ovocito_id) DO UPDATE SET
            estado_actual = EXCLUDED.estado_actual,
            calidad = EXCLUDED.calidad
    """, (
        o['id'], o['puncion_id'],
        o['created_at'].split(' ')[0] if o['created_at'] else None,
        o['estado'].lower() if o['estado'] else None,
        o['calidad'], o['donado'], fecha_key, estado_key
    ))

pg_conn.commit()
print(f"✅ {len(ovocitos)} ovocitos insertados\n")

# ====================================
# 11. POBLAR FACT_DONACION_SEMEN (Si tienes tabla)
# ====================================
print("💧 Poblando Fact_Donacion_Semen...")
# Asumiendo que tienes una tabla de donaciones de semen
try:
    donaciones = sqlite_conn.execute("""
        SELECT id, fecha_donacion, banco_origen, utilizado
        FROM Donacion_semen
    """).fetchall()
    
    for d in donaciones:
        fecha_key = get_tiempo_id(d['fecha_donacion'])
        
        pg_cursor.execute("""
            INSERT INTO Fact_Donacion_Semen (fecha_donacion, banco_origen, utilizado, fecha_key)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (d['fecha_donacion'], d['banco_origen'], d['utilizado'], fecha_key))
    
    pg_conn.commit()
    print(f"✅ {len(donaciones)} donaciones de semen insertadas\n")
except:
    print("⚠️ No se encontró tabla de donaciones de semen o está vacía\n")

# ====================================
# 12. POBLAR FACT_PAGO (Si tienes tabla de pagos)
# ====================================
print("💰 Poblando Fact_Pago...")
# Esto depende de si tienes una tabla de pagos
# Por ahora, lo dejamos como ejemplo
try:
    pagos = sqlite_conn.execute("""
        SELECT id, paciente_id, tratamiento_id, monto, monto_pagado, fecha_pago, obra_social
        FROM Pago_pago
    """).fetchall()
    
    for p in pagos:
        deuda = p['monto'] - (p['monto_pagado'] or 0)
        pagado = deuda <= 0
        
        fecha_key = get_tiempo_id(p['fecha_pago'])
        
        obra_social_key = None
        if p['obra_social']:
            pg_cursor.execute("SELECT obra_social_id FROM Dim_Obra_Social WHERE nombre = %s", (p['obra_social'],))
            res = pg_cursor.fetchone()
            obra_social_key = res[0] if res else None
        
        pg_cursor.execute("""
            INSERT INTO Fact_Pago (
                paciente_id, tratamiento_id, monto, monto_pagado, deuda, fecha_pago, pagado, obra_social,
                fecha_key, paciente_key, obra_social_key
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            p['paciente_id'], p['tratamiento_id'], p['monto'], p['monto_pagado'], deuda,
            p['fecha_pago'], pagado, p['obra_social'], fecha_key, p['paciente_id'], obra_social_key
        ))
    
    pg_conn.commit()
    print(f"✅ {len(pagos)} pagos insertados\n")
except:
    print("⚠️ No se encontró tabla de pagos o está vacía\n")

# ====================================
# CERRAR CONEXIONES
# ====================================
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("\n🎉 ETL COMPLETADO EXITOSAMENTE")
print("📊 Ahora puedes conectar Power BI a PostgreSQL y usar las vistas creadas")