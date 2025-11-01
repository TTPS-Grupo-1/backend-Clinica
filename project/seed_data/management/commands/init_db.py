from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from CustomUser.models import CustomUser
from Tratamiento.models import Tratamiento
from Monitoreo.models import Monitoreo

class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Eliminando datos existentes...'))
            Monitoreo.objects.all().delete()
            Tratamiento.objects.all().delete()
            CustomUser.objects.filter(rol__in=['PACIENTE', 'MEDICO']).delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos eliminados'))

        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando creación de datos...\n'))

        # =====================================
        # 1. CREAR MÉDICOS
        # =====================================
        self.stdout.write('👨‍⚕️  Creando médicos...')
        
        medicos_data = [
            {
                'email': 'dr.garcia@clinica.com',
                'first_name': 'Dr. Juan',
                'last_name': 'García',
                'dni': 30123456,
                'telefono': '2214567890',
            },
            {
                'email': 'dra.lopez@clinica.com',
                'first_name': 'Dra. María',
                'last_name': 'López',
                'dni': 31234567,
                'telefono': '2214567891',
            },
            {
                'email': 'dr.martinez@clinica.com',
                'first_name': 'Dr. Carlos',
                'last_name': 'Martínez',
                'dni': 32345678,
                'telefono': '2214567892',
            },
        ]

        medicos = []
        for data in medicos_data:
            medico, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'dni': data['dni'],
                    'telefono': data['telefono'],
                    'rol': 'MEDICO',
                    'is_active': True,
                }
            )
            if created:
                medico.set_password('12345678')
                medico.save()
                self.stdout.write(f'  ✅ {medico.first_name} {medico.last_name}')
            else:
                self.stdout.write(f'  ⚠️  {medico.first_name} {medico.last_name} (ya existía)')
            medicos.append(medico)

        # =====================================
        # 2. CREAR PACIENTES
        # =====================================
        self.stdout.write('\n👥 Creando pacientes...')
        
        pacientes_data = [
            {
                'email': 'ana.fernandez@email.com',
                'first_name': 'Ana',
                'last_name': 'Fernández',
                'dni': 40123456,
                'telefono': '2215678901',
            },
            {
                'email': 'lucia.gomez@email.com',
                'first_name': 'Lucía',
                'last_name': 'Gómez',
                'dni': 41234567,
                'telefono': '2215678902',
            },
            {
                'email': 'sofia.rodriguez@email.com',
                'first_name': 'Sofía',
                'last_name': 'Rodríguez',
                'dni': 42345678,
                'telefono': '2215678903',
            },
        ]

        pacientes = []
        for data in pacientes_data:
            paciente, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'dni': data['dni'],
                    'telefono': data['telefono'],
                    'rol': 'PACIENTE',
                    'is_active': True,
                }
            )
            if created:
                paciente.set_password('12345678')
                paciente.save()
                self.stdout.write(f'  ✅ {paciente.first_name} {paciente.last_name}')
            else:
                self.stdout.write(f'  ⚠️  {paciente.first_name} {paciente.last_name} (ya existía)')
            pacientes.append(paciente)

        # =====================================
        # 3. CREAR TRATAMIENTOS
        # =====================================
        self.stdout.write('\n💊 Creando tratamientos...')
        
        tratamientos = []
        for i, paciente in enumerate(pacientes):
            medico = medicos[i % len(medicos)]
            tratamiento, created = Tratamiento.objects.get_or_create(
                paciente=paciente,
                medico=medico,
                defaults={
                    'fecha_inicio': timezone.now().date() - timedelta(days=30),  # Hace 30 días
                    'activo': True,
                }
            )
            if created:
                self.stdout.write(
                    f'  ✅ Tratamiento #{tratamiento.id} - '
                    f'{paciente.first_name} con {medico.first_name}'
                )
            else:
                self.stdout.write(
                    f'  ⚠️  Tratamiento #{tratamiento.id} (ya existía)'
                )
            tratamientos.append(tratamiento)

        # =====================================
        # 4. CREAR MONITOREOS
        # =====================================
        self.stdout.write('\n📋 Creando monitoreos...')
        
        monitoreos_creados = 0
        for tratamiento in tratamientos:
            # Monitoreo pendiente (futuro)
            m1, created = Monitoreo.objects.get_or_create(
                tratamiento=tratamiento,
                fecha_atencion=timezone.now() + timedelta(days=3),
                defaults={
                    'descripcion': '',
                    'atendido': False,
                }
            )
            if created:
                monitoreos_creados += 1
                self.stdout.write(
                    f'  ✅ Monitoreo #{m1.id} - Pendiente (en 3 días) - '
                    f'{tratamiento.paciente.first_name}'
                )

            # Monitoreo para hoy
            m2, created = Monitoreo.objects.get_or_create(
                tratamiento=tratamiento,
                fecha_atencion=timezone.now() + timedelta(hours=2),
                defaults={
                    'descripcion': '',
                    'atendido': False,
                }
            )
            if created:
                monitoreos_creados += 1
                self.stdout.write(
                    f'  ✅ Monitoreo #{m2.id} - Para hoy (2 horas) - '
                    f'{tratamiento.paciente.first_name}'
                )

            # Monitoreo atendido
            m3, created = Monitoreo.objects.get_or_create(
                tratamiento=tratamiento,
                fecha_atencion=timezone.now() - timedelta(days=7),
                defaults={
                    'descripcion': 'Paciente presenta evolución favorable. Continuar con el tratamiento.',
                    'atendido': True,
                }
            )
            if created:
                monitoreos_creados += 1
                self.stdout.write(
                    f'  ✅ Monitoreo #{m3.id} - Atendido (hace 7 días) - '
                    f'{tratamiento.paciente.first_name}'
                )

        # =====================================
        # 5. RESUMEN
        # =====================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ BASE DE DATOS INICIALIZADA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📊 Resumen:')
        self.stdout.write(f'  👨‍⚕️  Médicos: {len(medicos)}')
        self.stdout.write(f'  👥 Pacientes: {len(pacientes)}')
        self.stdout.write(f'  💊 Tratamientos: {len(tratamientos)}')
        self.stdout.write(f'  📋 Monitoreos: {Monitoreo.objects.count()}')
        
        self.stdout.write(f'\n🔑 Credenciales de prueba (password: 12345678):')
        self.stdout.write('\n  Médicos:')
        for medico in medicos:
            self.stdout.write(f'    - {medico.email}')
        
        self.stdout.write('\n  Pacientes:')
        for paciente in pacientes:
            self.stdout.write(f'    - {paciente.email}')
        
        # Mostrar URLs de monitoreos pendientes
        monitoreos_pendientes = Monitoreo.objects.filter(atendido=False)[:3]
        if monitoreos_pendientes:
            self.stdout.write(f'\n🔗 URLs de prueba (monitoreos pendientes):')
            for m in monitoreos_pendientes:
                self.stdout.write(
                    f'  http://localhost:5173/monitoreos?monitoreoId={m.id}'
                )
        
        self.stdout.write(self.style.SUCCESS('\n✨ ¡Listo para usar!\n'))