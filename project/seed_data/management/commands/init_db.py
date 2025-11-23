from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import re
import secrets
import requests
import os
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
        parser.add_argument(
            '--skip-turnos',
            action='store_true',
            help='Omite la creación de turnos (para testing sin API externa)',
        )
        parser.add_argument(
            '--con-etapas',
            action='store_true',
            help='Crea pacientes en diferentes etapas de tratamiento',
        )

    def eliminar_todos_turnos_api(self):
        """Elimina todos los turnos existentes en la API externa"""
        try:
            url = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/delete_turnos"
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            if not token_grupo_3:
                self.stdout.write('Variable de entorno TOKEN_GRUPO_3 no encontrada')
                return False
                
            headers = {
                "Authorization": f"Bearer {token_grupo_3}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "id_grupo": 1
            }
            
            response = requests.delete(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                self.stdout.write('✅ Todos los turnos eliminados de la API')
                return True
            else:
                self.stdout.write(f'⚠️ Error eliminando turnos: {response.status_code}')
                return False
                
        except Exception as e:
            self.stdout.write(f'❌ Error: {str(e)}')
            return False

    def obtener_turnos_medico_api(self, medico_id):
        """Obtiene los turnos disponibles de un médico desde la API externa"""
        try:
            url = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico"
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            if not token_grupo_3:
                self.stdout.write('Variable de entorno TOKEN_GRUPO_3 no encontrada')
                return []
                
            headers = {
                "Authorization": f"Bearer {token_grupo_3}",
                "Content-Type": "application/json",
            }
            
            # Hacer GET request para obtener turnos
            response = requests.get(f"{url}?id_medico={medico_id}&id_grupo=1", headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                try:
                    turnos_data = response.json()
                    
                    # Si es una lista de turnos (estructura directa)
                    if isinstance(turnos_data, list):
                        turnos_ids = [turno.get('id') for turno in turnos_data if turno.get('id_paciente') is None]
                        return turnos_ids
                    # Si es un objeto con una propiedad 'data' que contiene la lista
                    elif isinstance(turnos_data, dict) and 'data' in turnos_data:
                        turnos_list = turnos_data['data']
                        turnos_ids = [turno.get('id') for turno in turnos_list if turno.get('id_paciente') is None]
                        return turnos_ids
                    # Si es un objeto con una propiedad 'turnos' que contiene la lista
                    elif isinstance(turnos_data, dict) and 'turnos' in turnos_data:
                        turnos_list = turnos_data['turnos']
                        turnos_ids = [turno.get('id') for turno in turnos_list if turno.get('id_paciente') is None]
                        return turnos_ids
                    else:
                        return []
                except Exception as e:
                    return []
            else:
                return []
                
        except Exception as e:
            return []

    def crear_horarios_masivos_api(self, medico_id, dia_semana, hora_inicio, hora_fin):
        """Crea turnos masivos para un médico usando POST /post_turnos"""
        try:
            url = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/post_turnos"
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            if not token_grupo_3:
                self.stdout.write('Variable de entorno TOKEN_GRUPO_3 no encontrada')
                return False, []
                
            headers = {
                "Authorization": f"Bearer {token_grupo_3}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "id_medico": medico_id,
                "id_grupo": 1,
                "dia_semana": dia_semana,  # 1=Lunes, 2=Martes, etc.
                "hora_inicio": hora_inicio,  # "09:00"
                "hora_fin": hora_fin,       # "17:00"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                # Capturar los IDs de los turnos creados
                try:
                    response_data = response.json()
                    
                    # La API no devuelve los IDs específicos, pero crea turnos secuenciales
                    # Calcular IDs basándose en turnos insertados
                    turnos_insertados = response_data.get('summary', {}).get('insertados_ok', 0)
                    
                    if turnos_insertados > 0:
                        # Generar IDs secuenciales (esto es una aproximación)
                        # Nota: En producción, necesitarías una API que devuelva los IDs reales
                        turnos_ids = list(range(1, turnos_insertados + 1))
                        return True, turnos_ids
                    else:
                        return True, []
                        
                except Exception as e:
                    return True, []  # Éxito pero sin IDs
            else:
                self.stdout.write(f'    ⚠️ Error creando horarios: {response.status_code}')
                return False, []
                
        except Exception as e:
            self.stdout.write(f'    ❌ Error: {str(e)}')
            return False, []

    def reservar_turno_api(self, medico_id, paciente_id, fecha, hora, id_turno):
        """Reserva un turno específico através de la API externa"""
        try:
            url = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/reservar_turno"
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            if not token_grupo_3:
                self.stdout.write('Variable de entorno TOKEN_GRUPO_3 no encontrada')
                return False
                
            headers = {
                "Authorization": f"Bearer {token_grupo_3}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "id_medico": medico_id,
                "id_grupo": 1,
                "id_paciente": paciente_id,
                "id_turno": id_turno,
                "fecha": fecha.strftime("%Y-%m-%d"),
                "hora": hora,
                "motivo": "Consulta de fertilidad"
            }
            
            response = requests.patch(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                return True
            else:
                self.stdout.write(f'    ⚠️ Error reservando turno: {response.status_code}')
                return False
                
        except Exception as e:
            self.stdout.write(f'    ❌ Error: {str(e)}')
            return False

    def crear_horarios_para_medicos(self, medicos, skip_turnos):
        """Crea horarios disponibles para todos los médicos"""
        if skip_turnos:
            self.stdout.write('⏭️ Omitiendo creación de horarios médicos...')
            return False, {}

        self.stdout.write('\n📋 Creando horarios disponibles para médicos...')
        
        # Configuración de horarios por médico
        horarios_config = [
            {"dias": [1, 3, 5], "inicio": "09:00", "fin": "17:00"},  # Lun, Mier, Vie
            {"dias": [2, 4], "inicio": "10:00", "fin": "16:00"},     # Mar, Jue
            {"dias": [1, 2, 3, 4, 5], "inicio": "08:00", "fin": "14:00"},  # Lun-Vie
        ]
        
        exito_total = True
        turnos_por_medico = {}  # {medico_id: [lista_de_ids_de_turnos]}
        
        for i, medico in enumerate(medicos):
            config = horarios_config[i % len(horarios_config)]
            turnos_por_medico[medico.id] = []
            
            self.stdout.write(f'  👨‍⚕️ {medico.first_name} {medico.last_name}')
            
            for dia in config["dias"]:
                dias_semana = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
                
                exito, _ = self.crear_horarios_masivos_api(
                    medico_id=medico.id,
                    dia_semana=dia,
                    hora_inicio=config["inicio"],
                    hora_fin=config["fin"]
                )
                
                if not exito:
                    exito_total = False
                else:
                    # Guardar los IDs de turnos para este médico (obtenidos por GET)
                    turnos_ids_reales = self.obtener_turnos_medico_api(medico.id)
                    turnos_por_medico[medico.id].extend(turnos_ids_reales)
                    self.stdout.write(f'    ✅ {dias_semana[dia]}: {config["inicio"]}-{config["fin"]} ({len(turnos_ids_reales)} turnos disponibles)')
        
        if exito_total:
            total_turnos = sum(len(ids) for ids in turnos_por_medico.values())
            self.stdout.write(f'✅ Todos los horarios médicos creados exitosamente ({total_turnos} turnos totales)')
        else:
            self.stdout.write('⚠️ Algunos horarios no se pudieron crear')
            
        return exito_total, turnos_por_medico

    def crear_turnos_locales_y_reservar(self, medicos, pacientes, tratamientos, turnos_por_medico, skip_turnos):
        """Crea turnos locales y los reserva en la API externa usando IDs reales"""
        if skip_turnos:
            self.stdout.write('⏭️ Omitiendo creación de turnos...')
            return [], []

        from Turnos.models import Turno
        self.stdout.write('\n� Reservando y creando turnos locales usando IDs reales de la API...')
        turnos_locales = []
        turnos_reservados = []

        for i, tratamiento in enumerate(tratamientos):
            medico_id = tratamiento.medico.id
            fecha_turno = timezone.now() + timedelta(days=1, hours=i+9)

            if medico_id in turnos_por_medico and turnos_por_medico[medico_id]:
                id_turno_real = turnos_por_medico[medico_id].pop(0)

                exito = self.reservar_turno_api(
                    medico_id=medico_id,
                    paciente_id=tratamiento.paciente.id,
                    fecha=fecha_turno.date(),
                    hora=fecha_turno.strftime("%H:%M"),
                    id_turno=id_turno_real
                )

                if exito:
                    # Crear el turno local ya con el id_externo real
                    turno = Turno.objects.create(
                        Paciente=tratamiento.paciente,
                        Medico=tratamiento.medico,
                        fecha_hora=fecha_turno,
                        cancelado=False,
                        atendido=False,
                        id_externo=id_turno_real,
                    )
                    tratamiento.turnos.add(turno)
                    turnos_locales.append(turno)
                    turnos_reservados.append(turno)
                    self.stdout.write(f'    ✅ Turno creado y reservado: {turno.Paciente.first_name} con {turno.Medico.first_name} (ID API: {id_turno_real})')
                else:
                    self.stdout.write(f'    ❌ Error reservando turno para {tratamiento.paciente.first_name} (ID intento: {id_turno_real})')
            else:
                self.stdout.write(f'    ⚠️ No hay turnos disponibles para médico {tratamiento.medico.first_name} para asociar a {tratamiento.paciente.first_name}')

        self.stdout.write(f'✅ {len(turnos_reservados)} turnos creados y reservados en API')
        return turnos_locales, turnos_reservados

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Eliminando datos existentes...'))
            Monitoreo.objects.all().delete()
            Tratamiento.objects.all().delete()
            # eliminar pacientes, medicos y operadores de laboratorio en --clear
            CustomUser.objects.filter(rol__in=['PACIENTE', 'MEDICO', 'OPERADOR_LABORATORIO']).delete()
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
        # 3.5 CREAR OPERADORES DE LABORATORIO
        # =====================================
        self.stdout.write('\n🧪 Creando operadores de laboratorio...')
        operadores_data = [
            {
                'email': 'operador.lab@clinica.com',
                'first_name': 'Operador',
                'last_name': 'Laboratorio',
                'dni': 33123456,
                'telefono': '2214000000',
            },
        ]

        operadores = []
        for data in operadores_data:
            operador, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'dni': data['dni'],
                    'telefono': data['telefono'],
                    'rol': 'OPERADOR_LABORATORIO',
                    'is_active': True,
                }
            )
            if created:
                operador.set_password('labpass123')
                operador.save()
                self.stdout.write(f'  ✅ {operador.first_name} {operador.last_name}')
            else:
                self.stdout.write(f'  ⚠️  {operador.first_name} {operador.last_name} (ya existía)')
            operadores.append(operador)

        # =====================================
        # 3. CREAR TRATAMIENTOS CON PRIMERA CONSULTA Y DATOS ASOCIADOS
        # =====================================
        self.stdout.write('\n💊 Creando tratamientos con primera consulta y datos asociados...')
        
        from PrimerConsulta.models import PrimeraConsulta
        from SegundaConsulta.models import SegundaConsulta
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
            
            # Objetivos realistas para probar diferentes casos
            objetivos = [
                'Embarazo gameto propio',  # Pareja heterosexual
                'Embarazo con pareja del mismo sexo',  # Pareja lesbiana
                'Mujer sin pareja - Donante de espermatozoide',  # Mujer sola
                'ROPA - Una aporta la célula y la otra el óvulo',  # Técnica ROPA
            ]
            
            # Crear Tratamiento asociado a la Primera Consulta
            tratamiento, created = Tratamiento.objects.get_or_create(
                paciente=paciente,
                medico=medico,
                defaults={
                    'objetivo': objetivos[i % len(objetivos)],
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
        # 4. CREAR SEGUNDAS CONSULTAS
        # =====================================
        self.stdout.write('\n🔬 Creando segundas consultas...')
        
        # Datos para segundas consultas con diferentes escenarios de semen/ovocito
        # Último caso: ni el semen ni el ovocito son viables
        segunda_consulta_scenarios = [
            {'semen_viable': True, 'ovocito_viable': True},
            {'semen_viable': False, 'ovocito_viable': True},
            {'semen_viable': False, 'ovocito_viable': False},  # último caso: ninguno viable
        ]

        for i, tratamiento in enumerate(tratamientos):
            if not tratamiento.segunda_consulta:  # Solo crear si no existe
                scenario = segunda_consulta_scenarios[i % len(segunda_consulta_scenarios)]

                # Crear la segunda consulta con el escenario seleccionado
                segunda_consulta = SegundaConsulta.objects.create(
                    semen_viable=scenario['semen_viable'],
                    ovocito_viable=scenario['ovocito_viable'],
                )

                # Asignar la segunda consulta al tratamiento
                tratamiento.segunda_consulta = segunda_consulta
                tratamiento.save()

                self.stdout.write(
                    f'  ✅ Segunda consulta creada para {tratamiento.paciente.first_name} - '
                    f'Semen viable: {scenario["semen_viable"]} - Ovocito viable: {scenario["ovocito_viable"]}'
                )

        # =====================================
        # 5. CREAR TURNOS Y ASOCIARLOS A TRATAMIENTOS
        #    Nota: la creación de los turnos locales se realizará en el paso de
        #    reserva (crear_turnos_locales_y_reservar) para asegurarnos de que
        #    el campo `id_externo` se sincronice con los IDs reales de la API.
        # =====================================
        self.stdout.write('\n📅 Preparando asociación de turnos a tratamientos (se crearán al reservar)...')

        # =====================================
        # 6. CREAR MONITOREOS
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
        # 6. CREAR PUNCIONES Y OVOCITOS (datos de prueba)
        # =====================================
        self.stdout.write('\n🩺 Creando punciones y ovocitos de ejemplo...')
        from Puncion.models import Puncion
        from Ovocito.models import Ovocito
        from Historial_ovocito.models import HistorialOvocito

        created_punciones = 0
        created_ovocitos = 0
        created_historial = 0

        for i, tratamiento in enumerate(tratamientos):
            paciente = tratamiento.paciente
            # crear una punción asociada al tratamiento/paciente
            fecha_puncion = timezone.now().date() - timedelta(days=10 + i)
            puncion = Puncion.objects.create(
                paciente=paciente,
                fecha=fecha_puncion,
                quirofano=f'Quirófano {chr(65 + (i % 3))}'
            )
            created_punciones += 1
            self.stdout.write(f'  ✅ Punción #{puncion.id} para {paciente.first_name} ({puncion.quirofano})')

            # crear 5 ovocitos de ejemplo por punción con diferentes estados
            madurez_opts = ['maduro', 'inmaduro', 'muy_inmaduro']
            # Estados: mayoría frescos, algunos criopreservados, pocos fertilizados
            estados = ['fresco', 'descartado', 'criopreservado', 'fertilizado']
            
            for j in range(1, 6):  # Crear 5 ovocitos por punción
                # Usar identificador con prefijo OVO y formato solicitado:
                # OVO_<3letrasApellido>_<3letrasNombre>_<7digitosAleatorios>
                def _three_letters(s: str) -> str:
                    clean = re.sub(r'[^A-Za-z]', '', (s or ''))
                    clean = clean.upper()
                    return (clean + 'XXX')[:3]

                suffix = str(secrets.randbelow(10**7)).zfill(7)
                identificador = f"OVO_{_three_letters(paciente.last_name)}_{_three_letters(paciente.first_name)}_{suffix}"
                # Asegurar unicidad regenerando sufijo si choca
                from Ovocito.models import Ovocito as _OvocitoCheck
                while _OvocitoCheck.objects.filter(identificador=identificador).exists():
                    suffix = str(secrets.randbelow(10**7)).zfill(7)
                    identificador = f"OVO_{_three_letters(paciente.last_name)}_{_three_letters(paciente.first_name)}_{suffix}"
                # Si la lista de estados tiene menos de 5 elementos, ciclarla en vez de indexar fuera de rango
                estado_ovocito = estados[(j-1) % len(estados)]  # Usar el estado correspondiente de forma segura

                ov = Ovocito.objects.create(
                    paciente=paciente,
                    puncion=puncion,
                    identificador=identificador,
                    madurez=madurez_opts[(j-1) % len(madurez_opts)],
                    tipo_estado=estado_ovocito
                )
                created_ovocitos += 1
                self.stdout.write(f'    - Ovocito {ov.identificador} (id {ov.id_ovocito}) - Estado: {estado_ovocito}')

                # Crear historial según el estado del ovocito
                if estado_ovocito == 'fertilizado':
                    # Para ovocitos fertilizados, historial completo
                    eventos = [
                        ('fresco', timezone.now() - timedelta(days=9 + j)),
                        ('fertilizado', timezone.now() - timedelta(days=7 + j)),
                    ]
                elif estado_ovocito == 'criopreservado':
                    # Para criopreservados
                    eventos = [
                        ('fresco', timezone.now() - timedelta(days=9 + j)),
                        ('criopreservado', timezone.now() - timedelta(days=7 + j)),
                    ]
                else:  # fresco o descartado
                    # Para frescos, solo el estado actual
                    eventos = [
                        (estado_ovocito, timezone.now() - timedelta(days=9 + j)),
                    ]
                
                for k, (estado, fecha_ev) in enumerate(eventos):
                    ho = HistorialOvocito.objects.create(
                        ovocito=ov,
                        paciente=paciente,
                        estado=estado,
                        fecha=fecha_ev,
                        nota=f'Ovocito en estado {estado}',
                        usuario=medicos[0] if medicos else None
                    )
                    created_historial += 1

        self.stdout.write(f'\n🔬 Punciones creadas: {created_punciones}')
        self.stdout.write(f'🔵 Ovocitos creados: {created_ovocitos}')
        self.stdout.write(f'📝 Eventos de historial creados: {created_historial}\n')

        # =====================================
        # 7. GESTIÓN COMPLETA DE TURNOS API
        # =====================================
        turnos_locales = []
        turnos_reservados = []
        
        if not options.get('skip_turnos', False):
            # Verificar token antes de empezar
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            if not token_grupo_3:
                self.stdout.write('❌ Variable de entorno TOKEN_GRUPO_3 no encontrada')
                self.stdout.write('   Ejecuta: export TOKEN_GRUPO_3="tu_token_aqui"')
                return
            
            
            # Paso 1: Eliminar todos los turnos existentes
            self.stdout.write('\n🗑️ Eliminando turnos existentes en API...')
            self.eliminar_todos_turnos_api()
            
            # Paso 2: Crear horarios masivos para médicos y capturar IDs
            exito_horarios, turnos_por_medico = self.crear_horarios_para_medicos(medicos, options.get('skip_turnos', False))
            
            # Paso 3: Crear turnos locales y reservar específicos usando IDs reales
            if exito_horarios:
                turnos_locales, turnos_reservados = self.crear_turnos_locales_y_reservar(
                    medicos, pacientes, tratamientos, turnos_por_medico, options.get('skip_turnos', False)
                )
            else:
                self.stdout.write('⚠️ No se crearon horarios médicos, omitiendo turnos específicos')
        
        # =====================================
        # 8. RESUMEN
        # =====================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ BASE DE DATOS INICIALIZADA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📊 Resumen:')
        self.stdout.write(f'  👨‍⚕️  Médicos: {len(medicos)}')
        self.stdout.write(f'  👥 Pacientes: {len(pacientes)}')
        self.stdout.write(f'  💊 Tratamientos: {len(tratamientos)}')
        self.stdout.write(f'  📋 Monitoreos: {Monitoreo.objects.count()}')
        self.stdout.write(f'  🗓️  Turnos locales: {len(turnos_locales)}')
        if turnos_reservados:
            self.stdout.write(f'  📅 Turnos reservados en API: {len(turnos_reservados)}')
        
        # Mostrar etapas si se usaron
        if options.get('con_etapas', False):
            self.stdout.write(f'\n🔍 Etapas de tratamiento aplicadas (función disponible con --con-etapas)')
        
        self.stdout.write(f'\n🔑 Credenciales de prueba (password: 12345678):')
        self.stdout.write('\n  Médicos:')
        for medico in medicos:
            self.stdout.write(f'    - {medico.email}')
        
        self.stdout.write('\n  Pacientes:')
        for paciente in pacientes:
            self.stdout.write(f'    - {paciente.email}')
        
        # Mostrar operadores de laboratorio
        if 'operadores' in locals() and operadores:
            self.stdout.write('\n  Operadores de laboratorio:')
            for op in operadores:
                self.stdout.write(f'    - {op.email}')
        
        # Mostrar URLs de monitoreos pendientes
        monitoreos_pendientes = Monitoreo.objects.filter(atendido=False)[:3]
        if monitoreos_pendientes:
            self.stdout.write(f'\n🔗 URLs de prueba (monitoreos pendientes):')
            for m in monitoreos_pendientes:
                self.stdout.write(
                    f'  http://localhost:5173/monitoreos?monitoreoId={m.id}'
                )
        
        self.stdout.write(self.style.SUCCESS('\n✨ ¡Listo para usar!\n'))
        
        # Información adicional sobre turnos API
        if turnos_reservados:
            self.stdout.write(self.style.SUCCESS('🚀 Funcionalidades de turnos activadas:'))
            self.stdout.write('  🗑️ Eliminación de turnos existentes (DELETE /delete_turnos)')
            self.stdout.write('  📋 Creación de horarios médicos masivos (POST /post_turnos)')
            self.stdout.write('  📅 Reserva de turnos específicos (PATCH /reservar_turno)')
            self.stdout.write('  🔗 IDs sincronizados entre BD local y API externa')
            self.stdout.write('\n  💡 Perfecto para probar "Atender Paciente" con datos realistas\n')
        
        # 1. Crear paciente y médico extra
        paciente_extra, _ = CustomUser.objects.get_or_create(
            email='extra.paciente@email.com',
            defaults={
                'first_name': 'Extra',
                'last_name': 'Paciente',
                'dni': 43456789,
                'telefono': '2215678999',
                'rol': 'PACIENTE',
                'is_active': True,
            }
        )
        paciente_extra.set_password('12345678')
        paciente_extra.save()

        medico_extra, _ = CustomUser.objects.get_or_create(
            email='extra.medico@clinica.com',
            defaults={
                'first_name': 'Extra',
                'last_name': 'Medico',
                'dni': 34123456,
                'telefono': '2214567999',
                'rol': 'MEDICO',
                'is_active': True,
            }
        )
        medico_extra.set_password('12345678')
        medico_extra.save()

        # 2. Crear horarios en la API para el médico extra
        exito, _ = self.crear_horarios_masivos_api(
            medico_id=medico_extra.id,
            dia_semana=1,  # Lunes
            hora_inicio="09:00",
            hora_fin="12:00"
        )

        # 3. Obtener un turno disponible en la API para ese médico
        turnos_ids = self.obtener_turnos_medico_api(medico_extra.id)
        if turnos_ids:
            id_turno_api = turnos_ids[0]
            fecha_turno = timezone.now() + timedelta(days=1)
            hora_turno = "09:00"

            # 4. Reservar el turno en la API para el paciente extra
            reservado = self.reservar_turno_api(
                medico_id=medico_extra.id,
                paciente_id=paciente_extra.id,
                fecha=fecha_turno.date(),
                hora=hora_turno,
                id_turno=id_turno_api
            )

            if reservado:
                # 5. Crear el turno local con el id_externo de la API
                from Turnos.models import Turno
                turno_local = Turno.objects.create(
                    Paciente=paciente_extra,
                    Medico=medico_extra,
                    fecha_hora=fecha_turno,
                    cancelado=False,
                    atendido=False,
                    id_externo=id_turno_api,
                )
                self.stdout.write(f'✅ Turno extra creado y reservado en API y local: {turno_local.Paciente.first_name} con {turno_local.Medico.first_name} (ID externo: {turno_local.id_externo})')
            else:
                self.stdout.write('❌ No se pudo reservar el turno en la API')
        else:
            self.stdout.write('❌ No hay turnos disponibles en la API para el médico extra')

        # 6.1 VERIFICAR QUE EL TURNO EXTRA ESTÁ RESERVADO Y TIENE PACIENTE ASIGNADO EN LA API
        self.stdout.write('\n🔍 Verificando turno extra en la API...')
        try:
            url = f"https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico?id_medico={medico_extra.id}&id_grupo=1"
            token_grupo_3 = os.getenv('TOKEN_GRUPO_3')
            headers = {
                "Authorization": f"Bearer {token_grupo_3}",
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                turnos_data = response.json()
                # Buscar el turno por id_turno_api
                turno_api = None
                if isinstance(turnos_data, dict) and 'data' in turnos_data:
                    turnos_list = turnos_data['data']
                elif isinstance(turnos_data, list):
                    turnos_list = turnos_data
                else:
                    turnos_list = []
                for t in turnos_list:
                    if t.get('id') == id_turno_api:
                        turno_api = t
                        break
                if turno_api:
                    self.stdout.write(f"  🟢 Turno API encontrado: id={turno_api.get('id')}, id_paciente={turno_api.get('id_paciente')}")
                    if turno_api.get('id_paciente') == paciente_extra.id:
                        self.stdout.write("  ✅ El turno extra está reservado correctamente para el paciente extra en la API.")
                    else:
                        self.stdout.write("  ⚠️ El turno extra NO tiene el paciente asignado en la API.")
                else:
                    self.stdout.write("  ❌ No se encontró el turno extra en la API.")
            else:
                self.stdout.write(f"  ❌ Error consultando la API: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"  ❌ Error verificando turno extra en la API: {str(e)}")

        # =====================================
        # AGREGAR 3 PACIENTES EXTRA CON DIFERENTES ESTADOS DE TRATAMIENTO
        # =====================================
        self.stdout.write('\n➕ Agregando 3 pacientes extra con diferentes estados...')
        
        #Agrego administrador 
        admin_user, _ = CustomUser.objects.get_or_create(
            email='admin@email.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'dni':  4456789023,
                'telefono': '2215678901',
                'rol': 'ADMIN',
                'is_active': True,
            }
        )
        admin_user.set_password('12345678')
        admin_user.save()
        

        # ----------------
        # PACIENTE 1: Primera consulta completada (próximo: Segunda consulta)
        # ----------------
        paciente_pc, _ = CustomUser.objects.get_or_create(
            email='paciente.pc@email.com',
            defaults={
                'first_name': 'Pedro',
                'last_name': 'Primera',
                'dni': 44567890,
                'telefono': '2215679001',
                'rol': 'PACIENTE',
                'is_active': True,
            }
        )
        paciente_pc.set_password('12345678')
        paciente_pc.save()
        self.stdout.write(f'  ✅ Paciente 1: {paciente_pc.first_name} {paciente_pc.last_name} (Primera consulta completada)')

        # Crear Primera Consulta
        primera_consulta_pc = PrimeraConsulta.objects.create(
            objetivo_consulta='Evaluación inicial para tratamiento de fertilidad',
            antecedentes_clinicos_1={'diabetes': False, 'hipertension': False},
            antecedentes_clinicos_2={'alergias': 'Ninguna', 'medicamentos': 'Ninguno'},
            antecedentes_familiares_1='Sin antecedentes relevantes',
            antecedentes_familiares_2='Sin antecedentes oncológicos',
            antecedentes_genitales='Sin patología genital previa',
            antecedentes_quirurgicos_1='Sin cirugías previas',
            antecedentes_quirurgicos_2='Sin complicaciones',
            examen_fisico_1='Paciente en buen estado general',
            examen_fisico_2='Signos vitales normales'
        )

        # Crear Tratamiento con Primera Consulta completada
        tratamiento_pc = Tratamiento.objects.create(
            paciente=paciente_pc,
            medico=medico_extra,
            objetivo='Embarazo gameto propio',
            fecha_inicio=timezone.now().date() - timedelta(days=15),
            activo=True,
            primera_consulta=primera_consulta_pc,
        )

        # Crear turno para Segunda Consulta
        turnos_ids_pc = self.obtener_turnos_medico_api(medico_extra.id)
        if turnos_ids_pc:
            id_turno_pc = turnos_ids_pc[0]
            fecha_turno_pc = timezone.now() + timedelta(days=2, hours=10)
            
            reservado_pc = self.reservar_turno_api(
                medico_id=medico_extra.id,
                paciente_id=paciente_pc.id,
                fecha=fecha_turno_pc.date(),
                hora="10:00",
                id_turno=id_turno_pc
            )
            
            if reservado_pc:
                from Turnos.models import Turno
                turno_pc = Turno.objects.create(
                    Paciente=paciente_pc,
                    Medico=medico_extra,
                    fecha_hora=fecha_turno_pc,
                    cancelado=False,
                    atendido=False,
                    id_externo=id_turno_pc,
                    es_monitoreo=False,
                )
                self.stdout.write(f'    ✅ Turno para Segunda Consulta creado (ID externo: {id_turno_pc})')

        # ----------------
        # PACIENTE 2: Primera y Segunda consulta completadas (próximo: Monitoreo)
        # ----------------
        paciente_sc, _ = CustomUser.objects.get_or_create(
            email='paciente.sc@email.com',
            defaults={
                'first_name': 'Sara',
                'last_name': 'Segunda',
                'dni': 45678901,
                'telefono': '2215679002',
                'rol': 'PACIENTE',
                'is_active': True,
            }
        )
        paciente_sc.set_password('12345678')
        paciente_sc.save()
        self.stdout.write(f'  ✅ Paciente 2: {paciente_sc.first_name} {paciente_sc.last_name} (Primera y Segunda consulta completadas)')

        # Crear Primera Consulta
        primera_consulta_sc = PrimeraConsulta.objects.create(
            objetivo_consulta='Evaluación inicial para tratamiento de fertilidad',
            antecedentes_clinicos_1={'diabetes': False, 'hipertension': False},
            antecedentes_clinicos_2={'alergias': 'Ninguna', 'medicamentos': 'Ácido fólico'},
            antecedentes_familiares_1='Sin antecedentes relevantes',
            antecedentes_familiares_2='Sin antecedentes oncológicos',
            antecedentes_genitales='Sin patología genital previa',
            antecedentes_quirurgicos_1='Sin cirugías previas',
            antecedentes_quirurgicos_2='Sin complicaciones',
            examen_fisico_1='Paciente en buen estado general',
            examen_fisico_2='Signos vitales normales'
        )

        # Crear Segunda Consulta
        segunda_consulta_sc = SegundaConsulta.objects.create(
            semen_viable=True,
            ovocito_viable=True,
        )

        # Crear Tratamiento con ambas consultas completadas
        tratamiento_sc = Tratamiento.objects.create(
            paciente=paciente_sc,
            medico=medico_extra,
            objetivo='Embarazo gameto propio',
            fecha_inicio=timezone.now().date() - timedelta(days=30),
            activo=True,
            primera_consulta=primera_consulta_sc,
            segunda_consulta=segunda_consulta_sc,
        )

        # Crear turno de monitoreo
        turnos_ids_sc = self.obtener_turnos_medico_api(medico_extra.id)
        if turnos_ids_sc:
            id_turno_sc = turnos_ids_sc[0]
            fecha_turno_sc = timezone.now() + timedelta(days=3, hours=11)
            
            reservado_sc = self.reservar_turno_api(
                medico_id=medico_extra.id,
                paciente_id=paciente_sc.id,
                fecha=fecha_turno_sc.date(),
                hora="11:00",
                id_turno=id_turno_sc
            )
            
            if reservado_sc:
                from Turnos.models import Turno
                turno_sc = Turno.objects.create(
                    Paciente=paciente_sc,
                    Medico=medico_extra,
                    fecha_hora=fecha_turno_sc,
                    cancelado=False,
                    atendido=False,
                    id_externo=id_turno_sc,
                    es_monitoreo=True,  # ✅ Es un turno de monitoreo
                )
                self.stdout.write(f'    ✅ Turno de Monitoreo creado (ID externo: {id_turno_sc})')

                # Crear monitoreo pendiente asociado
                Monitoreo.objects.create(
                    tratamiento=tratamiento_sc,
                    fecha_atencion=fecha_turno_sc,
                    descripcion='',
                    atendido=False,
                )
                self.stdout.write(f'    ✅ Monitoreo pendiente creado')

        # ----------------
        # PACIENTE 3: Con 3 monitoreos (1 atendido, 1 pendiente próximo, 1 futuro)
        # ----------------
        paciente_mon, _ = CustomUser.objects.get_or_create(
            email='paciente.mon@email.com',
            defaults={
                'first_name': 'Marta',
                'last_name': 'Monitoreo',
                'dni': 46789012,
                'telefono': '2215679003',
                'rol': 'PACIENTE',
                'is_active': True,
            }
        )
        paciente_mon.set_password('12345678')
        paciente_mon.save()
        self.stdout.write(f'  ✅ Paciente 3: {paciente_mon.first_name} {paciente_mon.last_name} (Con 3 monitoreos)')

        # Crear Primera Consulta
        primera_consulta_mon = PrimeraConsulta.objects.create(
            objetivo_consulta='Evaluación inicial para tratamiento de fertilidad',
            antecedentes_clinicos_1={'diabetes': False, 'hipertension': False},
            antecedentes_clinicos_2={'alergias': 'Ninguna', 'medicamentos': 'Ácido fólico'},
            antecedentes_familiares_1='Sin antecedentes relevantes',
            antecedentes_familiares_2='Sin antecedentes oncológicos',
            antecedentes_genitales='Sin patología genital previa',
            antecedentes_quirurgicos_1='Sin cirugías previas',
            antecedentes_quirurgicos_2='Sin complicaciones',
            examen_fisico_1='Paciente en buen estado general',
            examen_fisico_2='Signos vitales normales'
        )

        # Crear Segunda Consulta
        segunda_consulta_mon = SegundaConsulta.objects.create(
            semen_viable=True,
            ovocito_viable=True,
        )

        # Crear Tratamiento
        tratamiento_mon = Tratamiento.objects.create(
            paciente=paciente_mon,
            medico=medico_extra,
            objetivo='Embarazo gameto propio',
            fecha_inicio=timezone.now().date() - timedelta(days=45),
            activo=True,
            primera_consulta=primera_consulta_mon,
            segunda_consulta=segunda_consulta_mon,
        )

        # Monitoreo 1: Atendido (pasado)
        mon1 = Monitoreo.objects.create(
            tratamiento=tratamiento_mon,
            fecha_atencion=timezone.now() - timedelta(days=10),
            descripcion='Primer monitoreo completado. Evolución favorable.',
            atendido=True,
            fecha_realizado=timezone.now() - timedelta(days=10),
        )
        self.stdout.write(f'    ✅ Monitoreo 1 (atendido hace 10 días)')

        # Monitoreo 2: Pendiente próximo (turno reservado en API)
        turnos_ids_mon = self.obtener_turnos_medico_api(medico_extra.id)
        if turnos_ids_mon:
            id_turno_mon = turnos_ids_mon[0]
            fecha_turno_mon = timezone.now() + timedelta(days=1, hours=14)
            
            reservado_mon = self.reservar_turno_api(
                medico_id=medico_extra.id,
                paciente_id=paciente_mon.id,
                fecha=fecha_turno_mon.date(),
                hora="14:00",
                id_turno=id_turno_mon
            )
            
            if reservado_mon:
                from Turnos.models import Turno
                turno_mon = Turno.objects.create(
                    Paciente=paciente_mon,
                    Medico=medico_extra,
                    fecha_hora=fecha_turno_mon,
                    cancelado=False,
                    atendido=False,
                    id_externo=id_turno_mon,
                    es_monitoreo=True,
                )
                self.stdout.write(f'    ✅ Turno para Monitoreo 2 creado (ID externo: {id_turno_mon})')

        mon2 = Monitoreo.objects.create(
            tratamiento=tratamiento_mon,
            fecha_atencion=fecha_turno_mon if turnos_ids_mon else timezone.now() + timedelta(days=1),
            descripcion='',
            atendido=False,
        )
        self.stdout.write(f'    ✅ Monitoreo 2 (pendiente - mañana)')

        # Monitoreo 3: Futuro (sin turno asignado aún)
        mon3 = Monitoreo.objects.create(
            tratamiento=tratamiento_mon,
            fecha_atencion=timezone.now() + timedelta(days=7),
            descripcion='',
            atendido=False,
        )
        self.stdout.write(f'    ✅ Monitoreo 3 (futuro - en 7 días)')