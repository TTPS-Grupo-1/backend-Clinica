-- ====================================
-- POBLAR DIMENSIONES BÁSICAS
-- ====================================

-- POBLAR DIM_TECNICA
INSERT INTO Dim_Tecnica (nombre, descripcion) VALUES 
    ('FIV', 'Fertilización In Vitro'),
    ('ICSI', 'Inyección Intracitoplasmática de Espermatozoides'),
    ('IA', 'Inseminación Artificial')
ON CONFLICT (nombre) DO NOTHING;

-- POBLAR DIM_CALIDAD
INSERT INTO Dim_Calidad (calidad) VALUES ('A'), ('B'), ('C'), ('D')
ON CONFLICT (calidad) DO NOTHING;

-- POBLAR DIM_ESTADO_EMBRION
INSERT INTO Dim_Estado_Embrion (estado) VALUES 
    ('fresco'), ('criopreservado'), ('transferido'), ('descartado')
ON CONFLICT (estado) DO NOTHING;

-- POBLAR DIM_ESTADO_OVOCITO
INSERT INTO Dim_Estado_Ovocito (estado) VALUES 
    ('fresco'), ('criopreservado'), ('usado'), ('descartado')
ON CONFLICT (estado) DO NOTHING;

COMMIT;