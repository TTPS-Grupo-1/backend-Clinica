from django.core.management.base import BaseCommand
from django.db import transaction
from CustomUser.models import CustomUser
from datetime import date


class Command(BaseCommand):
    help = 'Poblar la base de datos con usuarios de ejemplo (médicos, pacientes, admin)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar usuarios existentes antes de crear nuevos (excepto superusers)',
        )
        parser.add_argument(
            '--only',
            choices=['medicos', 'pacientes', 'admin'],
            help='Crear solo un tipo específico de usuarios',
        )

    def handle(self, *args, **options):
        self.stdout.write('🏥 Iniciando seed completo de usuarios...')

        # Si se especifica --clear, eliminar usuarios existentes (excepto superusers)
        if options['clear']:
            self.stdout.write('🗑️  Eliminando usuarios existentes (excepto superusers)...')
            CustomUser.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('Usuarios existentes eliminados.'))

        created_total = 0

        # MÉDICOS
        if not options['only'] or options['only'] == 'medicos':
            created_total += self.create_medicos()

        # PACIENTES
        if not options['only'] or options['only'] == 'pacientes':
            created_total += self.create_pacientes()

        # ADMINISTRATIVOS
        if not options['only'] or options['only'] == 'admin':
            created_total += self.create_administrativos()

        # Resumen final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 SEED COMPLETO FINALIZADO'))
        self.stdout.write(f'📊 Total de usuarios creados/actualizados: {created_total}')

    def create_medicos(self):
        self.stdout.write('👨‍⚕️ Creando médicos...')
        
        medicos_data = [
            {
                'email': 'dr.martinez@clinicaenvy.com',
                'first_name': 'Roberto',
                'last_name': 'Martínez',
                'dni': '12345678',
                'telefono': '1154778899',
                'rol': 'MEDICO',
                'password': 'medico123'
            },
            {
                'email': 'dra.lopez@clinicaenvy.com',
                'first_name': 'María',
                'last_name': 'López',
                'dni': '23456789',
                'telefono': '1145889966',
                'rol': 'MEDICO',
                'password': 'medico123'
            },
            {
                'email': 'dr.garcia@clinicaenvy.com',
                'first_name': 'Carlos',
                'last_name': 'García',
                'dni': '34567890',
                'telefono': '1156990077',
                'rol': 'MEDICO',
                'password': 'medico123'
            },
            {
                'email': 'dra.rodriguez@clinicaenvy.com',
                'first_name': 'Ana',
                'last_name': 'Rodríguez',
                'dni': '45678901',
                'telefono': '1167001188',
                'rol': 'MEDICO',
                'password': 'medico123'
            },
            {
                'email': 'dr.fernandez@clinicaenvy.com',
                'first_name': 'Alejandro',
                'last_name': 'Fernández',
                'dni': '56789012',
                'telefono': '1178112299',
                'rol': 'MEDICO',
                'password': 'medico123'
            },
            # Director Médico
            {
                'email': 'dr.director@clinicaenvy.com',
                'first_name': 'Eduardo',
                'last_name': 'Villareal',
                'dni': '11223344',
                'telefono': '1134778855',
                'rol': 'DIRECTOR_MEDICO',
                'password': 'director123'
            }
        ]

        return self._create_users(medicos_data, '👨‍⚕️')

    def create_pacientes(self):
        self.stdout.write('🤱 Creando pacientes...')
        
        pacientes_data = [
            {
                'email': 'maria.gonzalez@email.com',
                'first_name': 'María',
                'last_name': 'González',
                'dni': '33444555',
                'telefono': '1187654321',
                'rol': 'PACIENTE',
                'fecha_nacimiento': date(1985, 3, 15),
                'sexo': 'F',
                'obra_social': 123456,
                'numero_afiliado': 'OS-123456',
                'password': 'paciente123'
            },
            {
                'email': 'lucia.perez@email.com',
                'first_name': 'Lucía',
                'last_name': 'Pérez',
                'dni': '44555666',
                'telefono': '1198765432',
                'rol': 'PACIENTE',
                'fecha_nacimiento': date(1990, 7, 22),
                'sexo': 'F',
                'obra_social': 789012,
                'numero_afiliado': 'OS-789012',
                'password': 'paciente123'
            },
            {
                'email': 'juan.martinez@email.com',
                'first_name': 'Juan',
                'last_name': 'Martínez',
                'dni': '55666777',
                'telefono': '1109876543',
                'rol': 'PACIENTE',
                'fecha_nacimiento': date(1988, 11, 8),
                'sexo': 'M',
                'obra_social': 345678,
                'numero_afiliado': 'OS-345678',
                'password': 'paciente123'
            },
            {
                'email': 'sofia.ramirez@email.com',
                'first_name': 'Sofía',
                'last_name': 'Ramírez',
                'dni': '66777888',
                'telefono': '1120987654',
                'rol': 'PACIENTE',
                'fecha_nacimiento': date(1992, 5, 30),
                'sexo': 'F',
                'obra_social': 901234,
                'numero_afiliado': 'OS-901234',
                'password': 'paciente123'
            },
            {
                'email': 'gabriel.torres@email.com',
                'first_name': 'Gabriel',
                'last_name': 'Torres',
                'dni': '77888999',
                'telefono': '1131098765',
                'rol': 'PACIENTE',
                'fecha_nacimiento': date(1987, 12, 14),
                'sexo': 'M',
                'obra_social': 567890,
                'numero_afiliado': 'OS-567890',
                'password': 'paciente123'
            }
        ]

        return self._create_users(pacientes_data, '🤱')

    def create_administrativos(self):
        self.stdout.write('🏢 Creando personal administrativo...')
        
        admin_data = [
            {
                'email': 'admin@clinicaenvy.com',
                'first_name': 'Carmen',
                'last_name': 'Administradora',
                'dni': '20304050',
                'telefono': '1142109876',
                'rol': 'ADMIN',
                'password': 'admin123'
            },
            {
                'email': 'laboratorio@clinicaenvy.com',
                'first_name': 'Técnico',
                'last_name': 'Laboratorio',
                'dni': '30405060',
                'telefono': '1153210987',
                'rol': 'LAB_OPERATOR',
                'password': 'lab123'
            }
        ]

        return self._create_users(admin_data, '🏢')

    def _create_users(self, users_data, emoji):
        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for user_data in users_data:
                email = user_data['email']
                password = user_data.pop('password')
                
                try:
                    user, created = CustomUser.objects.get_or_create(
                        email=email,
                        defaults=user_data
                    )
                    
                    if created:
                        user.set_password(password)
                        user.save()
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'{emoji} ✅ Creado: {user.first_name} {user.last_name} ({user.rol})')
                        )
                    else:
                        for key, value in user_data.items():
                            setattr(user, key, value)
                        user.set_password(password)
                        user.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'{emoji} 🔄 Actualizado: {user.first_name} {user.last_name} ({user.rol})')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'{emoji} ❌ Error creando {email}: {str(e)}')
                    )

        self.stdout.write(f'{emoji} Creados: {created_count}, Actualizados: {updated_count}')
        return created_count + updated_count