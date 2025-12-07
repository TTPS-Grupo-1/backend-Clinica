$PSQL = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
$USER = "postgres"
$COMMON_PASSWORDS = @("postgres", "admin", "password", "123456", "root", "12345678", "1234", "postgres123")

Write-Host "Probando contrasenas comunes de PostgreSQL..." -ForegroundColor Cyan
Write-Host ""

foreach ($pass in $COMMON_PASSWORDS) {
    $env:PGPASSWORD = $pass
    Write-Host "Probando: $pass ... " -NoNewline -ForegroundColor Yellow
    
    $result = & $PSQL -U $USER -c "SELECT 1;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ENCONTRADA!" -ForegroundColor Green
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "Tu contrasena de PostgreSQL es: $pass" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Guarda esta contrasena y ejecuta:" -ForegroundColor Yellow
        Write-Host '$env:PGPASSWORD = "' + $pass + '"' -ForegroundColor Cyan
        Write-Host ".\test_setup.ps1" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "NO" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "No se encontro la contrasena entre las mas comunes." -ForegroundColor Yellow
Write-Host ""
Write-Host "Opciones:" -ForegroundColor Cyan
Write-Host "1. Piensa que contrasena usaste al instalar PostgreSQL" -ForegroundColor White
Write-Host "2. Revisa si tienes la contrasena guardada en algun archivo" -ForegroundColor White
Write-Host "3. Resetea la contrasena editando pg_hba.conf" -ForegroundColor White
