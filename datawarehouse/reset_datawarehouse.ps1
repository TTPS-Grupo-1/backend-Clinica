# ====================================
# SCRIPT DE RESET COMPLETO DEL DW
# ====================================

Write-Host "🗑️  Eliminando base de datos existente..." -ForegroundColor Yellow
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS clinica_datawarehouse;"

Write-Host "🏗️  Creando nueva base de datos..." -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE clinica_datawarehouse WITH OWNER = postgres ENCODING = 'UTF8';"

Write-Host "📊 Creando dimensiones..." -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_dimensions.sql

Write-Host "📈 Creando tablas de hechos..." -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d clinica_datawarehouse -f create_facts.sql

Write-Host "📋 Poblando catálogos estáticos..." -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d clinica_datawarehouse -f populate_dimensions.sql

Write-Host "🎲 Generando datos de prueba..." -ForegroundColor Green
python generate_test_data.py

Write-Host "✅ Reset completo finalizado!" -ForegroundColor Green
