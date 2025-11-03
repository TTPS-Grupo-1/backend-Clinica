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
        # 3. CREAR TRATAMIENTOS CON PRIMERA CONSULTA Y DATOS ASOCIADOS
        # =====================================
        self.stdout.write('\n💊 Creando tratamientos con primera consulta y datos asociados...')
        
        from PrimerConsulta.models import PrimeraConsulta
        from Fenotipo.models import Fenotipo
        from ResultadoEstudio.models import ResultadoEstudio
        from AntecedentesGinecologicos.models import AntecedentesGinecologicos
        from AntecedentesPersonales.models import AntecedentesPersonales
        
        tratamientos = []
        for i, paciente in enumerate(pacientes):
            medico = medicos[i % len(medicos)]
            
            # Crear Primera Consulta única para cada paciente
            primera_consulta = PrimeraConsulta.objects.create(
                objetivo_consulta=f'Evaluación inicial para tratamiento de fertilidad de {paciente.first_name}',
                antecedentes_clinicos_1={'diabetes': False, 'hipertension': True if i % 2 == 0 else False},
                antecedentes_clinicos_2={'alergias': 'Ninguna conocida', 'medicamentos': 'Ácido fólico'},
                antecedentes_familiares_1='Historia familiar de diabetes en línea materna',
                antecedentes_familiares_2='Sin antecedentes oncológicos relevantes',
                antecedentes_genitales='Sin patología genital previa',
                antecedentes_quirurgicos_1='Apendicectomía en 2018' if i % 3 == 0 else 'Sin cirugías previas',
                antecedentes_quirurgicos_2='Sin complicaciones postoperatorias',
                examen_fisico_1='Paciente en buen estado general, peso 65kg, altura 165cm',
                examen_fisico_2='Signos vitales normales, exploración ginecológica normal'
            )
            
            # Crear Tratamiento asociado a la Primera Consulta
            tratamiento, created = Tratamiento.objects.get_or_create(
                paciente=paciente,
                medico=medico,
                defaults={
                    'objetivo': f'Tratamiento de fertilidad para {paciente.first_name}',
                    'fecha_inicio': timezone.now().date() - timedelta(days=30),
                    'activo': True,
                    'primera_consulta': primera_consulta,
                }
            )
            
            if created:
                self.stdout.write(
                    f'  ✅ Tratamiento #{tratamiento.id} - '
                    f'{paciente.first_name} con {medico.first_name}'
                )
                
                # Crear Fenotipo asociado a la Primera Consulta
                fenotipo_data = [
                    {'color_ojos': 'marrón', 'color_pelo': 'castaño', 'tipo_pelo': 'lacio', 'altura_cm': 165, 'complexion_corporal': 'normal', 'rasgos_etnicos': 'europeo'},
                    {'color_ojos': 'verde', 'color_pelo': 'rubio', 'tipo_pelo': 'ondulado', 'altura_cm': 170, 'complexion_corporal': 'delgada', 'rasgos_etnicos': 'latino'},
                    {'color_ojos': 'azul', 'color_pelo': 'negro', 'tipo_pelo': 'rizado', 'altura_cm': 160, 'complexion_corporal': 'robusta', 'rasgos_etnicos': 'afrodescendiente'}
                ]
                
                fenotipo = Fenotipo.objects.create(
                    consulta=primera_consulta,
                    **fenotipo_data[i % len(fenotipo_data)]
                )
                self.stdout.write(f'    ✅ Fenotipo creado para {paciente.first_name}')
                
                # Crear Antecedentes Ginecológicos
                antec_gine = AntecedentesGinecologicos.objects.create(
                    consulta=primera_consulta,
                    menarca=12 + (i % 3),  # Entre 12 y 14 años
                    ciclo_menstrual=28 + (i % 3),  # Entre 28 y 30 días
                    regularidad='regular' if i % 2 == 0 else 'irregular',
                    duracion_menstrual_dias=5 + (i % 2),  # Entre 5 y 6 días
                    caracteristicas_sangrado=['leve', 'moderado', 'abundante'][i % 3],
                    g=i % 3,  # Número de embarazos
                    p=i % 2,  # Partos
                    ab=0 if i % 3 == 0 else 1,  # Abortos
                    st=0,  # Embarazos ectópicos
                )
                self.stdout.write(f'    ✅ Antecedentes Ginecológicos creados para {paciente.first_name}')
                
                # Crear Antecedentes Personales
                antec_pers = AntecedentesPersonales.objects.create(
                    consulta=primera_consulta,
                    fuma_pack_dias='0' if i % 2 == 0 else '2.5',
                    consume_alcohol='Ocasional, vino' if i % 3 == 0 else 'No consume',
                    drogas_recreativas='No consume',
                    observaciones_habitos='Realiza ejercicio regularmente, dieta balanceada'
                )
                self.stdout.write(f'    ✅ Antecedentes Personales creados para {paciente.first_name}')
                
                # Crear Resultados de Estudios
                estudios_data = [
                    {'nombre_estudio': 'FSH', 'tipo_estudio': 'Hormonal', 'valor': '8.5 mUI/mL', 'persona': 'PACIENTE'},
                    {'nombre_estudio': 'LH', 'tipo_estudio': 'Hormonal', 'valor': '6.2 mUI/mL', 'persona': 'PACIENTE'},
                    {'nombre_estudio': 'AMH', 'tipo_estudio': 'Hormonal', 'valor': '2.1 ng/mL', 'persona': 'PACIENTE'},
                    {'nombre_estudio': 'Espermiograma', 'tipo_estudio': 'Seminograma', 'valor': 'Normozoospermia', 'persona': 'ACOMPAÑANTE'},
                ]
                
                for estudio_data in estudios_data:
                    resultado = ResultadoEstudio.objects.create(
                        consulta=primera_consulta,
                        **estudio_data
                    )
                
                self.stdout.write(f'    ✅ Resultados de Estudios creados para {paciente.first_name}')
                
            else:
                self.stdout.write(
                    f'  ⚠️  Tratamiento #{tratamiento.id} (ya existía)'
                )
            tratamientos.append(tratamiento)

        # =====================================
        # 4. CREAR TURNOS Y ASOCIARLOS A TRATAMIENTOS
        # =====================================
        self.stdout.write('\n📅 Creando turnos y asociándolos a tratamientos...')
        
        from Turnos.models import Turno
        
        for i, tratamiento in enumerate(tratamientos):
            # Crear un turno para cada tratamiento
            turno, created = Turno.objects.get_or_create(
                Paciente=tratamiento.paciente,
                Medico=tratamiento.medico,
                defaults={
                    'fecha_hora': timezone.now() + timedelta(days=1, hours=i+9),  # Turnos al día siguiente a las 9, 10, 11 AM
                    'cancelado': False,
                    'atendido': False,
                    'id_externo': 1000 + i,  # ID único para cada turno
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Turno #{turno.id} creado para {tratamiento.paciente.first_name}')
            
            # Asociar el turno al tratamiento
            tratamiento.turnos.add(turno)
            self.stdout.write(f'    ✅ Turno asociado al Tratamiento #{tratamiento.id}')

        # =====================================
        # 5. CREAR MONITOREOS
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
        # 6. RESUMEN
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