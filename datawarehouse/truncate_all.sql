-- ====================================
-- LIMPIAR TODAS LAS TABLAS
-- ====================================

-- Desactivar restricciones de claves foráneas temporalmente
SET session_replication_role = 'replica';

-- Truncar tablas de hechos (primero porque tienen FKs)
TRUNCATE TABLE Fact_Paciente_Actividad CASCADE;
TRUNCATE TABLE Fact_Pago CASCADE;
TRUNCATE TABLE Fact_Donacion_Semen CASCADE;
TRUNCATE TABLE Fact_Embrion CASCADE;
TRUNCATE TABLE Fact_Ovocito CASCADE;
TRUNCATE TABLE Fact_Monitoreo CASCADE;
TRUNCATE TABLE Fact_Fertilizacion CASCADE;
TRUNCATE TABLE Fact_Tratamiento CASCADE;

-- Truncar dimensiones dinámicas (se repoblarán con ETL o generate_test_data)
TRUNCATE TABLE Dim_Tiempo RESTART IDENTITY CASCADE;
TRUNCATE TABLE Dim_Medico CASCADE;
TRUNCATE TABLE Dim_Paciente CASCADE;
TRUNCATE TABLE Dim_Operador CASCADE;
TRUNCATE TABLE Dim_Objetivo RESTART IDENTITY CASCADE;
TRUNCATE TABLE Dim_Obra_Social RESTART IDENTITY CASCADE;

-- NO truncar catálogos estáticos (Dim_Tecnica, Dim_Calidad, Dim_Estado_*)
-- Estos se poblaron con populate_dimensions.sql y no cambian

-- Reactivar restricciones
SET session_replication_role = 'origin';

-- Mensaje de confirmación
SELECT 'Todas las tablas han sido limpiadas' AS status;
