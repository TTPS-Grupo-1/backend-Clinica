# Script de prueba del Data Warehouse
# Asegurate de haber configurado la variable de entorno PGPASSWORD antes de ejecutar
# O usa: $env:PGPASSWORD = "tu_contrasena"

$PSQL = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
$DB_NAME = "clinica_datawarehouse"
$USER = "postgres"

Write-Host "[DW] PRUEBA DEL DATA WAREHOUSE - Clinica de Fertilidad" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Paso 1: Verificar conexion a PostgreSQL
Write-Host "`n[1/6] Verificando conexion a PostgreSQL..." -ForegroundColor Yellow
& $PSQL -U $USER -c "SELECT version()" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Conexion exitosa a PostgreSQL" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error conectando a PostgreSQL. Verifica usuario/contrasena" -ForegroundColor Red
    Write-Host "[TIP] Ejecuta primero: `$env:PGPASSWORD = 'tu_contrasena'" -ForegroundColor Yellow
    exit 1
}

# Paso 2: Verificar/Crear base de datos
Write-Host "`n[2/6] Verificando base de datos '$DB_NAME'..." -ForegroundColor Yellow
$dbExists = & $PSQL -U $USER -lqt | Select-String -Pattern $DB_NAME
if ($dbExists) {
    Write-Host "[OK] Base de datos '$DB_NAME' ya existe" -ForegroundColor Green
} else {
    Write-Host "[INFO] Base de datos no existe. Creando..." -ForegroundColor Yellow
    & $PSQL -U $USER -c "CREATE DATABASE $DB_NAME"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Base de datos '$DB_NAME' creada" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error creando base de datos" -ForegroundColor Red
        exit 1
    }
}

# Paso 3: Crear dimensiones
Write-Host "`n[3/6] Creando tablas de dimensiones..." -ForegroundColor Yellow
& $PSQL -U $USER -d $DB_NAME -f "create_dimensions.sql" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dimensiones creadas" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error creando dimensiones" -ForegroundColor Red
}

# Paso 4: Poblar dimensiones basicas
Write-Host "`n[4/6] Poblando dimensiones basicas..." -ForegroundColor Yellow
& $PSQL -U $USER -d $DB_NAME -f "populate_dimensions.sql" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dimensiones pobladas" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error poblando dimensiones" -ForegroundColor Red
}

# Paso 5: Crear tablas de hechos
Write-Host "`n[5/6] Creando tablas de hechos..." -ForegroundColor Yellow
& $PSQL -U $USER -d $DB_NAME -f "create_facts.sql" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Tablas de hechos creadas" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error creando tablas de hechos" -ForegroundColor Red
}

# Paso 6: Verificar tablas creadas
Write-Host "`n[6/6] Verificando tablas creadas..." -ForegroundColor Yellow
$tables = & $PSQL -U $USER -d $DB_NAME -c "\dt" 2>&1
if ($tables -match "dim_tiempo" -and $tables -match "fact_tratamiento") {
    Write-Host "[OK] Todas las tablas fueron creadas correctamente" -ForegroundColor Green
    
    # Mostrar resumen
    Write-Host "`n[RESUMEN] Tablas creadas:" -ForegroundColor Cyan
    & $PSQL -U $USER -d $DB_NAME -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename" -A -t | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor White
    }
} else {
    Write-Host "[WARN] Algunas tablas pueden no haberse creado" -ForegroundColor Yellow
}

# Instrucciones siguientes
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "[OK] SETUP COMPLETADO" -ForegroundColor Green
Write-Host "`n[PROXIMOS PASOS]:" -ForegroundColor Yellow
Write-Host "1. Configura la contrasena en etl_script.py (linea 7)" -ForegroundColor White
Write-Host "2. Ejecuta: python etl_script.py" -ForegroundColor White
Write-Host "3. Conecta Power BI a: localhost / clinica_datawarehouse" -ForegroundColor White
Write-Host "`n[TIP] Para ver los datos:" -ForegroundColor Yellow
Write-Host "   & '$PSQL' -U $USER -d $DB_NAME" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
