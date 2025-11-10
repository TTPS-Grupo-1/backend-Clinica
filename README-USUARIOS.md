
# Usuarios de prueba

Este archivo lista las credenciales que el script de seed (`init_db`) crea por defecto para pruebas locales.

| Email | Password | Rol | Notas |
|---|---:|---|---|
| dr.garcia@clinica.com | `12345678` | MEDICO | Médico de ejemplo
| dra.lopez@clinica.com | `12345678` | MEDICO | Médica de ejemplo
| dr.martinez@clinica.com | `12345678` | MEDICO | Médico de ejemplo
| ana.fernandez@email.com | `12345678` | PACIENTE | Paciente de prueba
| lucia.gomez@email.com | `12345678` | PACIENTE | Paciente de prueba
| sofia.rodriguez@email.com | `12345678` | PACIENTE | Paciente de prueba
| operador.lab@clinica.com | `labpass123` | OPERADOR_LABORATORIO | Operador de laboratorio (tests/manuales)


Cómo (re)crear estos usuarios

1. Desde la raíz del proyecto Django ejecuta el comando de seed:

```bash
python manage.py init_db
```

2. Si quieres limpiar la base de datos y recrear los usuarios (útil en dev):

```bash
python manage.py init_db --clear
```

Notas
- Si la base de datos ya contiene usuarios con los mismos emails, `init_db` no sobrescribirá la contraseña de esos usuarios (salvo que los elimines con `--clear`).
- Las contraseñas aquí son intencionalmente simples para desarrollo. No uses estas credenciales en producción.
- El rol canónico para el operador de laboratorio es `OPERADOR_LABORATORIO`.
