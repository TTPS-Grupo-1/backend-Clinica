-- ========================================
-- CONSULTAS SQL PARA ANÁLISIS DEL DATA WAREHOUSE
-- Base de datos: clinica_datawarehouse
-- ========================================

-- 1️⃣ TASA DE ÉXITO POR TÉCNICA DE FERTILIZACIÓN
-- Muestra el porcentaje de éxito de cada técnica (ICSI, FIV, IA)
SELECT 
    dt.nombre,
    COUNT(*) as total_fertilizaciones,
    SUM(CASE WHEN ff.ovocitos_fertilizados > 0 THEN 1 ELSE 0 END) as exitosas,
    ROUND(100.0 * SUM(CASE WHEN ff.ovocitos_fertilizados > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito_porcentaje
FROM Fact_Fertilizacion ff
JOIN Dim_Tecnica dt ON ff.tecnica_id = dt.tecnica_id
GROUP BY dt.nombre
ORDER BY tasa_exito_porcentaje DESC;


-- 2️⃣ EVOLUCIÓN DE TRATAMIENTOS POR MES
-- Muestra la cantidad de tratamientos iniciados por mes y año
SELECT 
    dti.anio,
    dti.mes,
    dti.nombre_mes,
    COUNT(*) as cantidad_tratamientos,
    SUM(CASE WHEN ft.estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) as exitosos,
    SUM(CASE WHEN ft.estado_tratamiento = 'Activo' THEN 1 ELSE 0 END) as activos,
    SUM(CASE WHEN ft.estado_tratamiento = 'Cancelado' THEN 1 ELSE 0 END) as cancelados
FROM Fact_Tratamiento ft
JOIN Dim_Tiempo dti ON ft.tiempo_key = dti.tiempo_key
GROUP BY dti.anio, dti.mes, dti.nombre_mes
ORDER BY dti.anio, dti.mes;


-- 3️⃣ RENDIMIENTO POR MÉDICO
-- Califica a los médicos por cantidad de tratamientos y tasa de éxito
SELECT 
    dm.nombre_completo as medico,
    dm.especialidad,
    COUNT(DISTINCT ft.tratamiento_id) as total_tratamientos,
    SUM(CASE WHEN ft.estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) as tratamientos_exitosos,
    ROUND(100.0 * SUM(CASE WHEN ft.estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito_porcentaje,
    AVG(ft.costo_total) as costo_promedio
FROM Fact_Tratamiento ft
JOIN Dim_Medico dm ON ft.medico_key = dm.medico_key
GROUP BY dm.medico_key, dm.nombre_completo, dm.especialidad
HAVING COUNT(*) > 5  -- Solo médicos con más de 5 tratamientos
ORDER BY tasa_exito_porcentaje DESC;


-- 4️⃣ DISTRIBUCIÓN DE CALIDAD DE EMBRIONES
-- Analiza la calidad de los embriones generados
SELECT 
    dc.grado_calidad,
    dc.descripcion_calidad,
    COUNT(*) as cantidad_embriones,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as porcentaje_del_total,
    SUM(CASE WHEN dee.descripcion_estado = 'Transferido' THEN 1 ELSE 0 END) as transferidos,
    SUM(CASE WHEN dee.descripcion_estado = 'Criopreservado' THEN 1 ELSE 0 END) as criopreservados
FROM Fact_Embrion fe
JOIN Dim_Calidad dc ON fe.calidad_key = dc.calidad_key
JOIN Dim_Estado_Embrion dee ON fe.estado_embrion_key = dee.estado_embrion_key
GROUP BY dc.calidad_key, dc.grado_calidad, dc.descripcion_calidad
ORDER BY dc.grado_calidad;


-- 5️⃣ ANÁLISIS DE PACIENTES POR EDAD Y OBJETIVO
-- Cruza la edad de los pacientes con el objetivo del tratamiento
SELECT 
    CASE 
        WHEN dp.edad < 30 THEN 'Menor de 30'
        WHEN dp.edad BETWEEN 30 AND 35 THEN '30-35 años'
        WHEN dp.edad BETWEEN 36 AND 40 THEN '36-40 años'
        WHEN dp.edad > 40 THEN 'Mayor de 40'
    END as rango_edad,
    dobj.descripcion_objetivo,
    COUNT(*) as cantidad_tratamientos,
    AVG(ft.costo_total) as costo_promedio
FROM Fact_Tratamiento ft
JOIN Dim_Paciente dp ON ft.paciente_key = dp.paciente_key
JOIN Dim_Objetivo dobj ON ft.objetivo_key = dobj.objetivo_key
GROUP BY rango_edad, dobj.descripcion_objetivo
ORDER BY rango_edad, cantidad_tratamientos DESC;


-- 6️⃣ OVOCITOS: CANTIDAD Y CALIDAD
-- Analiza la cantidad de ovocitos recuperados y su madurez
SELECT 
    deo.descripcion_estado,
    COUNT(*) as total_ovocitos,
    ROUND(AVG(fo.cantidad_ovocitos), 2) as promedio_cantidad,
    MIN(fo.cantidad_ovocitos) as minimo,
    MAX(fo.cantidad_ovocitos) as maximo
FROM Fact_Ovocito fo
JOIN Dim_Estado_Ovocito deo ON fo.estado_ovocito_key = deo.estado_ovocito_key
GROUP BY deo.estado_ovocito_key, deo.descripcion_estado
ORDER BY total_ovocitos DESC;


-- 7️⃣ INGRESOS TOTALES POR MES (PAGOS)
-- Suma de pagos recibidos por mes
SELECT 
    dt.anio,
    dt.nombre_mes,
    COUNT(*) as cantidad_pagos,
    SUM(fp.monto_pagado) as total_recaudado,
    ROUND(AVG(fp.monto_pagado), 2) as promedio_pago
FROM Fact_Pago fp
JOIN Dim_Tiempo dt ON fp.tiempo_key = dt.tiempo_key
GROUP BY dt.anio, dt.mes, dt.nombre_mes
ORDER BY dt.anio, dt.mes;


-- 8️⃣ COMPARACIÓN: OBRA SOCIAL VS PARTICULAR
-- Compara costos y resultados entre pacientes con obra social y particulares
SELECT 
    CASE 
        WHEN dos.nombre_obra_social = 'Particular' THEN 'Particular'
        ELSE 'Con Obra Social'
    END as tipo_paciente,
    COUNT(DISTINCT ft.tratamiento_id) as cantidad_tratamientos,
    ROUND(AVG(ft.costo_total), 2) as costo_promedio,
    SUM(CASE WHEN ft.estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) as exitosos,
    ROUND(100.0 * SUM(CASE WHEN ft.estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito
FROM Fact_Tratamiento ft
JOIN Dim_Paciente dp ON ft.paciente_key = dp.paciente_key
JOIN Dim_Obra_Social dos ON dp.obra_social_key = dos.obra_social_key
GROUP BY tipo_paciente;


-- 9️⃣ MONITOREO: SEGUIMIENTO DE TRATAMIENTOS
-- Cuenta cuántos monitoreos se realizan por tratamiento en promedio
SELECT 
    COUNT(DISTINCT fm.tratamiento_id) as tratamientos_monitoreados,
    COUNT(*) as total_monitoreos,
    ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT fm.tratamiento_id), 2) as promedio_monitoreos_por_tratamiento
FROM Fact_Monitoreo fm;


-- 🔟 TOP 10 PACIENTES CON MÁS ACTIVIDAD
-- Identifica los pacientes con más registros en el sistema
SELECT 
    dp.nombre_completo,
    dp.edad,
    dp.obra_social,
    COUNT(*) as cantidad_registros,
    MIN(dt.fecha) as primera_actividad,
    MAX(dt.fecha) as ultima_actividad
FROM Fact_Paciente_Actividad fpa
JOIN Dim_Paciente dp ON fpa.paciente_key = dp.paciente_key
JOIN Dim_Tiempo dt ON fpa.tiempo_key = dt.tiempo_key
GROUP BY dp.paciente_key, dp.nombre_completo, dp.edad, dp.obra_social
ORDER BY cantidad_registros DESC
LIMIT 10;


-- ========================================
-- 🎯 CONSULTAS AVANZADAS (KPIs)
-- ========================================

-- 📊 KPI 1: TASA DE ÉXITO GENERAL DE LA CLÍNICA
SELECT 
    COUNT(*) as total_tratamientos,
    SUM(CASE WHEN estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) as exitosos,
    SUM(CASE WHEN estado_tratamiento = 'Activo' THEN 1 ELSE 0 END) as activos,
    SUM(CASE WHEN estado_tratamiento = 'Cancelado' THEN 1 ELSE 0 END) as cancelados,
    ROUND(100.0 * SUM(CASE WHEN estado_tratamiento = 'Exitoso' THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito_general
FROM Fact_Tratamiento;


-- 📊 KPI 2: INGRESOS TOTALES Y COSTO PROMEDIO
SELECT 
    SUM(costo_total) as ingresos_totales,
    ROUND(AVG(costo_total), 2) as costo_promedio_tratamiento,
    MIN(costo_total) as tratamiento_mas_economico,
    MAX(costo_total) as tratamiento_mas_costoso
FROM Fact_Tratamiento;


-- 📊 KPI 3: CANTIDAD DE EMBRIONES POR FERTILIZACIÓN
SELECT 
    COUNT(DISTINCT ff.fertilizacion_id) as total_fertilizaciones,
    COUNT(DISTINCT fe.embrion_id) as total_embriones,
    ROUND(CAST(COUNT(DISTINCT fe.embrion_id) AS FLOAT) / COUNT(DISTINCT ff.fertilizacion_id), 2) as promedio_embriones_por_fertilizacion
FROM Fact_Fertilizacion ff
LEFT JOIN Fact_Embrion fe ON ff.fertilizacion_id = fe.fertilizacion_id;


-- 📊 KPI 4: MÉDICO MÁS PRODUCTIVO DEL MES ACTUAL
SELECT 
    dm.nombre_completo,
    dm.especialidad,
    COUNT(*) as tratamientos_este_mes,
    SUM(ft.costo_total) as facturacion_total
FROM Fact_Tratamiento ft
JOIN Dim_Medico dm ON ft.medico_key = dm.medico_key
JOIN Dim_Tiempo dt ON ft.tiempo_key = dt.tiempo_key
WHERE dt.mes = EXTRACT(MONTH FROM CURRENT_DATE)
  AND dt.anio = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY dm.medico_key, dm.nombre_completo, dm.especialidad
ORDER BY tratamientos_este_mes DESC
LIMIT 1;


-- ========================================
-- 💡 TIPS PARA POWER BI
-- ========================================
-- 1. Importa estas consultas como "Vista previa de datos" en Power BI
-- 2. Crea medidas calculadas (DAX) basadas en estos KPIs
-- 3. Usa filtros de fecha (Dim_Tiempo) para gráficos dinámicos
-- 4. Relaciona las tablas Fact_* con Dim_* por *_key
-- 5. Crea jerarquías: Año > Trimestre > Mes > Día
