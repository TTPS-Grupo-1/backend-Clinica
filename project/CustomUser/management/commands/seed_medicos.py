from django.core.management.base import BaseCommand
from django.db import transaction
from CustomUser.models import CustomUser
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Poblar la base de datos con médicos de la clínica de fertilidad'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar médicos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write('🏥 Iniciando seed de médicos de la clínica...')

        # Si se especifica --clear, eliminar médicos existentes
        if options['clear']:
            self.stdout.write('🗑️  Eliminando médicos existentes...')
            CustomUser.objects.filter(rol='MEDICO').delete()
            self.stdout.write(self.style.WARNING('Médicos existentes eliminados.'))

        # Datos de médicos especialistas en fertilidad
        medicos_data = [
            {
                'email': 'dr.martinez@clinicaenvy.com',
                'first_name': 'Roberto',
                'last_name': 'Martínez',
                'dni': '12345678',
                'telefono': '1154778899',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dra.lopez@clinicaenvy.com',
                'first_name': 'María',
                'last_name': 'López',
                'dni': '23456789',
                'telefono': '1145889966',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dr.garcia@clinicaenvy.com',
                'first_name': 'Carlos',
                'last_name': 'García',
                'dni': '34567890',
                'telefono': '1156990077',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dra.rodriguez@clinicaenvy.com',
                'first_name': 'Ana',
                'last_name': 'Rodríguez',
                'dni': '45678901',
                'telefono': '1167001188',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dr.fernandez@clinicaenvy.com',
                'first_name': 'Alejandro',
                'last_name': 'Fernández',
                'dni': '56789012',
                'telefono': '1178112299',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dra.sanchez@clinicaenvy.com',
                'first_name': 'Laura',
                'last_name': 'Sánchez',
                'dni': '67890123',
                'telefono': '1189223300',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dr.torres@clinicaenvy.com',
                'first_name': 'Miguel',
                'last_name': 'Torres',
                'dni': '78901234',
                'telefono': '1190334411',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dra.morales@clinicaenvy.com',
                'first_name': 'Patricia',
                'last_name': 'Morales',
                'dni': '89012345',
                'telefono': '1101445522',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dr.vargas@clinicaenvy.com',
                'first_name': 'Diego',
                'last_name': 'Vargas',
                'dni': '90123456',
                'telefono': '1112556633',
                'rol': 'MEDICO',
                'is_active': True,
                'password': 'medico123'
            },
            {
                'email': 'dra.castro@clinicaenvy.com',
                'first_name': 'Elena',
                'last_name': 'Castro',
                'dni': '01234567',
                'telefono': '1123667744',
                'rol': 'MEDICO',
                'is_active': True,
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
                'is_active': True,
                'password': 'director123'
            }
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for medico_data in medicos_data:
                email = medico_data['email']
                password = medico_data.pop('password')  # Extraemos password del dict
                
                try:
                    # Verificar si el médico ya existe
                    medico, created = CustomUser.objects.get_or_create(
                        email=email,
                        defaults=medico_data
                    )
                    
                    if created:
                        # Si es nuevo, establecer la contraseña
                        medico.set_password(password)
                        medico.save()
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Creado: Dr(a). {medico.first_name} {medico.last_name}')
                        )
                    else:
                        # Si ya existe, actualizar los datos (opcional)
                        for key, value in medico_data.items():
                            setattr(medico, key, value)
                        medico.set_password(password)  # Actualizar contraseña también
                        medico.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Actualizado: Dr(a). {medico.first_name} {medico.last_name}')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error creando {email}: {str(e)}')
                    )

        # Resumen final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 SEED COMPLETADO'))
        self.stdout.write(f'📊 Médicos creados: {created_count}')
        self.stdout.write(f'🔄 Médicos actualizados: {updated_count}')
        self.stdout.write('')
        self.stdout.write('📋 CREDENCIALES DE ACCESO:')
        self.stdout.write('• Médicos: password "medico123"')
        self.stdout.write('• Director: password "director123"')
        self.stdout.write('')
        self.stdout.write('🔐 EMAILS DE MÉDICOS CREADOS:')
        for medico_data in medicos_data:
            rol_display = '👨‍⚕️' if medico_data['rol'] == 'MEDICO' else '🏥'
            self.stdout.write(f'{rol_display} {medico_data["email"]} - Dr(a). {medico_data["first_name"]} {medico_data["last_name"]}')