-- ====================================
-- CREAR TABLAS DE HECHOS
-- ====================================

-- FACT_TRATAMIENTO
CREATE TABLE IF NOT EXISTS Fact_Tratamiento (
    tratamiento_id INT PRIMARY KEY,
    paciente_id INT NOT NULL,
    medico_id INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_finalizacion DATE,
    objetivo VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    motivo_finalizacion VARCHAR(200),
    exitoso BOOLEAN,
    etapa_alcanzada VARCHAR(50), -- 'Primera Consulta', 'Segunda Consulta', 'Punción', 'Fertilización', 'Transferencia'
    duracion_dias INT,
    
    -- Etapas completadas
    primera_consulta_completada BOOLEAN DEFAULT FALSE,
    segunda_consulta_completada BOOLEAN DEFAULT FALSE,
    puncion_realizada BOOLEAN DEFAULT FALSE,
    fertilizacion_realizada BOOLEAN DEFAULT FALSE,
    transferencia_realizada BOOLEAN DEFAULT FALSE,
    
    -- Claves foráneas
    fecha_inicio_key INT REFERENCES Dim_Tiempo(tiempo_id),
    fecha_fin_key INT REFERENCES Dim_Tiempo(tiempo_id),
    medico_key INT REFERENCES Dim_Medico(medico_id),
    paciente_key INT REFERENCES Dim_Paciente(paciente_id),
    objetivo_key INT REFERENCES Dim_Objetivo(objetivo_id)
);

-- FACT_FERTILIZACION
CREATE TABLE IF NOT EXISTS Fact_Fertilizacion (
    fertilizacion_id INT PRIMARY KEY,
    tratamiento_id INT NOT NULL REFERENCES Fact_Tratamiento(tratamiento_id),
    operador_id INT NOT NULL,
    fecha_fertilizacion DATE NOT NULL,
    tecnica VARCHAR(50),
    resultado VARCHAR(50), -- 'Exitosa', 'No exitosa'
    ovocitos_utilizados INT DEFAULT 0,
    embriones_generados INT DEFAULT 0,
    tasa_fertilizacion DECIMAL(5,2),
    exitosa BOOLEAN, -- TRUE si resultado = 'Exitosa'
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    operador_key INT REFERENCES Dim_Operador(operador_id),
    tecnica_key INT REFERENCES Dim_Tecnica(tecnica_id)
);

-- FACT_MONITOREO
CREATE TABLE IF NOT EXISTS Fact_Monitoreo (
    monitoreo_id SERIAL PRIMARY KEY,
    tratamiento_id INT NOT NULL REFERENCES Fact_Tratamiento(tratamiento_id),
    fecha_monitoreo DATE NOT NULL,
    numero_monitoreo INT, -- 1, 2, 3...
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    tratamiento_key INT REFERENCES Fact_Tratamiento(tratamiento_id)
);

-- FACT_EMBRION
CREATE TABLE IF NOT EXISTS Fact_Embrion (
    embrion_id INT PRIMARY KEY,
    fertilizacion_id INT NOT NULL REFERENCES Fact_Fertilizacion(fertilizacion_id),
    fecha_creacion DATE NOT NULL,
    estado_actual VARCHAR(50), -- 'fresco', 'criopreservado', 'transferido', 'descartado'
    calidad VARCHAR(10),
    pgt_realizado BOOLEAN DEFAULT FALSE,
    resultado_pgt VARCHAR(50),
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    calidad_key INT REFERENCES Dim_Calidad(calidad_id),
    estado_key INT REFERENCES Dim_Estado_Embrion(estado_id)
);

-- FACT_OVOCITO
CREATE TABLE IF NOT EXISTS Fact_Ovocito (
    ovocito_id INT PRIMARY KEY,
    puncion_id INT,
    fecha_extraccion DATE,
    estado_actual VARCHAR(50), -- 'fresco', 'criopreservado', 'usado', 'descartado'
    calidad VARCHAR(10),
    donado BOOLEAN DEFAULT FALSE,
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    estado_key INT REFERENCES Dim_Estado_Ovocito(estado_id)
);

-- FACT_DONACION_SEMEN
CREATE TABLE IF NOT EXISTS Fact_Donacion_Semen (
    donacion_id SERIAL PRIMARY KEY,
    fecha_donacion DATE NOT NULL,
    banco_origen VARCHAR(100),
    utilizado BOOLEAN DEFAULT FALSE,
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id)
);

-- FACT_PAGO (Para deudas)
CREATE TABLE IF NOT EXISTS Fact_Pago (
    pago_id SERIAL PRIMARY KEY,
    paciente_id INT NOT NULL,
    tratamiento_id INT REFERENCES Fact_Tratamiento(tratamiento_id),
    monto DECIMAL(10,2),
    monto_pagado DECIMAL(10,2) DEFAULT 0,
    deuda DECIMAL(10,2), -- monto - monto_pagado
    fecha_pago DATE,
    pagado BOOLEAN DEFAULT FALSE,
    obra_social VARCHAR(100),
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    paciente_key INT REFERENCES Dim_Paciente(paciente_id),
    obra_social_key INT REFERENCES Dim_Obra_Social(obra_social_id)
);

-- FACT_PACIENTE_ACTIVIDAD (Para altas)
CREATE TABLE IF NOT EXISTS Fact_Paciente_Actividad (
    actividad_id SERIAL PRIMARY KEY,
    paciente_id INT NOT NULL,
    fecha_evento DATE NOT NULL,
    tipo_evento VARCHAR(50), -- 'Alta', 'Baja'
    
    -- Claves foráneas
    fecha_key INT REFERENCES Dim_Tiempo(tiempo_id),
    paciente_key INT REFERENCES Dim_Paciente(paciente_id)
);

COMMIT;