#!/bin/bash

# ====================================
# SCRIPT DE RESET COMPLETO DEL DW
# ====================================

echo "🗑️  Eliminando base de datos existente..."
"/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -c "DROP DATABASE IF EXISTS clinica_datawarehouse;"

echo "🏗️  Creando nueva base de datos..."
"/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -c "CREATE DATABASE clinica_datawarehouse WITH OWNER = postgres ENCODING = 'UTF8';"

echo "📊 Creando dimensiones..."
"/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -d clinica_datawarehouse -f create_dimensions.sql

echo "📈 Creando tablas de hechos..."
"/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -d clinica_datawarehouse -f create_facts.sql

echo "📋 Poblando catálogos estáticos..."
"/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -d clinica_datawarehouse -f populate_dimensions.sql

echo "🎲 Generando datos de prueba..."
python generate_test_data.py

echo "✅ Reset completo finalizado!"
