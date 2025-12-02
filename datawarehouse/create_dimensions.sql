-- ====================================
-- CREAR DIMENSIONES
-- ====================================

-- DIM_TIEMPO
CREATE TABLE IF NOT EXISTS Dim_Tiempo (
    tiempo_id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    dia INT NOT NULL,
    mes INT NOT NULL,
    trimestre INT NOT NULL,
    anio INT NOT NULL,  -- ✅ Cambiado de "año" a "anio"
    nombre_mes VARCHAR(20),
    nombre_dia_semana VARCHAR(20),
    es_fin_semana BOOLEAN
);

-- DIM_MEDICO
CREATE TABLE IF NOT EXISTS Dim_Medico (
    medico_id INT PRIMARY KEY,
    dni INT UNIQUE NOT NULL,
    nombre_completo VARCHAR(200),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    eliminado BOOLEAN DEFAULT FALSE,
    is_director BOOLEAN DEFAULT FALSE
);

-- DIM_PACIENTE
CREATE TABLE IF NOT EXISTS Dim_Paciente (
    paciente_id INT PRIMARY KEY,
    dni INT UNIQUE NOT NULL,
    nombre_completo VARCHAR(200),
    edad INT,
    sexo VARCHAR(10),
    obra_social VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE
);

-- DIM_OPERADOR
CREATE TABLE IF NOT EXISTS Dim_Operador (
    operador_id INT PRIMARY KEY,
    nombre_completo VARCHAR(200),
    email VARCHAR(100)
);

-- DIM_TECNICA
CREATE TABLE IF NOT EXISTS Dim_Tecnica (
    tecnica_id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- DIM_OBJETIVO
CREATE TABLE IF NOT EXISTS Dim_Objetivo (
    objetivo_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- DIM_CALIDAD
CREATE TABLE IF NOT EXISTS Dim_Calidad (
    calidad_id SERIAL PRIMARY KEY,
    calidad VARCHAR(10) UNIQUE NOT NULL
);

-- DIM_ESTADO_EMBRION
CREATE TABLE IF NOT EXISTS Dim_Estado_Embrion (
    estado_id SERIAL PRIMARY KEY,
    estado VARCHAR(50) UNIQUE NOT NULL
);

-- DIM_ESTADO_OVOCITO
CREATE TABLE IF NOT EXISTS Dim_Estado_Ovocito (
    estado_id SERIAL PRIMARY KEY,
    estado VARCHAR(50) UNIQUE NOT NULL
);

-- DIM_OBRA_SOCIAL
CREATE TABLE IF NOT EXISTS Dim_Obra_Social (
    obra_social_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

COMMIT;