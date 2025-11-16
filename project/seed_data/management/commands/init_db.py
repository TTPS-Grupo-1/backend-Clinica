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

    def crear_turnos_masivos_api(self, medico_id, dia_semana, hora_inicio, hora_fin):
        """Crea turnos masivos para un médico usando POST /post_turnos"""
        try:
            url = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/post_turnos"
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
                "dia_semana": dia_semana,  # 1=Lunes, 2=Martes, etc.
                "hora_inicio": hora_inicio,  # "09:00"
                "hora_fin": hora_fin,       # "17:00"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(response.text)
            if response.status_code == 200:
                self.stdout.write(f'    ✅ Turnos masivos creados: Médico {medico_id} - {dia_semana} de {hora_inicio} a {hora_fin}')
                return True
            else:
                self.stdout.write(f'    ⚠️ Error creando turnos masivos: {response.status_code}')
                return False
                
        except Exception as e:
            self.stdout.write(f'    ❌ Error: {str(e)}')
            return False

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
            print(response.text)
            if response.status_code == 200:
                self.stdout.write(f'    ✅ Turno reservado: Médico {medico_id} - Paciente {paciente_id}')
                return True
            else:
                self.stdout.write(f'    ⚠️ Error reservando turno: {response.status_code}')
                return False
                
        except Exception as e:
            self.stdout.write(f'    ❌ Error: {str(e)}')
            return False

    def obtener_etapa_tratamiento(self, indice):
        """Define en qué etapa está cada paciente"""
        etapas = [
            "primera_consulta",    # Solo primera consulta
            "segunda_consulta",    # Con segunda consulta
            "estudios",           # Con estudios realizados
            "monitoreo",          # En monitoreo
            "puncion",           # Con punción realizada
            "fertilizacion",     # Con fertilización
            "transferencia",     # Listo para transferencia
            "seguimiento"        # En seguimiento post-transferencia
        ]
        return etapas[indice % len(etapas)]

    def crear_datos_por_etapa(self, tratamiento, etapa, indice):
        """Crea datos específicos según la etapa del tratamiento"""
        
        # Etapa 2: Segunda consulta
        if etapa in ['segunda_consulta', 'estudios', 'monitoreo', 'puncion', 'fertilizacion', 'transferencia', 'seguimiento']:
            from SegundaConsulta.models import SegundaConsulta
            if not tratamiento.segunda_consulta:  # Solo crear si no existe
                segunda_consulta = SegundaConsulta.objects.create(
                    semen_viable=True,
                    ovocito_viable=True,
                    observaciones=f'Segunda consulta - Caso {indice + 1}',
                )
                tratamiento.segunda_consulta = segunda_consulta
                tratamiento.save()
        
        # Etapa 3: Estudios
        if etapa in ['estudios', 'monitoreo', 'puncion', 'fertilizacion', 'transferencia', 'seguimiento']:
            from ResultadoEstudio.models import ResultadoEstudio
            ResultadoEstudio.objects.get_or_create(
                consulta=tratamiento.primera_consulta,
                nombre_estudio='Análisis hormonal - Etapa',
                defaults={
                    'tipo_estudio': 'Hormonal',
                    'valor': 'Valores normales',
                    'persona': 'PACIENTE'
                }
            )
        
        # Etapa 4: Monitoreo
        if etapa in ['monitoreo', 'puncion', 'fertilizacion', 'transferencia', 'seguimiento']:
            Monitoreo.objects.get_or_create(
                tratamiento=tratamiento,
                fecha_atencion=timezone.now() - timedelta(days=10 + indice),
                defaults={
                    'descripcion': f'Monitoreo - Desarrollo folicular adecuado',
                    'atendido': True,
                }
            )
        
        # Etapa 5: Punción y Ovocitos
        if etapa in ['puncion', 'fertilizacion', 'transferencia', 'seguimiento']:
            from Puncion.models import Puncion
            from Ovocito.models import Ovocito
            
            puncion, created = Puncion.objects.get_or_create(
                paciente=tratamiento.paciente,
                fecha=timezone.now().date() - timedelta(days=5 + indice),
                defaults={
                    'quirofano': f'Quirófano {chr(65 + (indice % 3))}'
                }
            )
            
            if created:
                for i in range(3 + indice % 3):
                    def _three_letters(s: str) -> str:
                        clean = re.sub(r'[^A-Za-z]', '', (s or ''))
                        clean = clean.upper()
                        return (clean + 'XXX')[:3]

                    suffix = str(secrets.randbelow(10**7)).zfill(7)
                    identificador = f"OVO_{_three_letters(tratamiento.paciente.last_name)}_{_three_letters(tratamiento.paciente.first_name)}_{suffix}"
                    
                    Ovocito.objects.create(
                        paciente=tratamiento.paciente,
                        puncion=puncion,
                        identificador=identificador,
                        madurez=['muy_inmaduro', 'inmaduro', 'maduro'][i % 3],
                        tipo_estado='fresco',
                    )
        
        # Etapa 6: Fertilización y Embriones
        if etapa in ['fertilizacion', 'transferencia', 'seguimiento']:
            from Fertilizacion.models import Fertilizacion
            from Embrion.models import Embrion
            from Ovocito.models import Ovocito
            
            ovocitos = Ovocito.objects.filter(
                paciente=tratamiento.paciente
            )
            
            for i, ovocito in enumerate(ovocitos[:2]):  # Fertilizar máximo 2
                fertilizacion, created = Fertilizacion.objects.get_or_create(
                    ovocito=ovocito,
                    defaults={
                        'fecha_fertilizacion': timezone.now().date() - timedelta(days=3 + indice),
                        'metodo_fertilizacion': ['ICSI', 'FIV'][i % 2],
                        'exitosa': True,
                    }
                )
                
                if created and fertilizacion.exitosa:
                    Embrion.objects.create(
                        fertilizacion=fertilizacion,
                        codigo=f'EMB-{tratamiento.id}-{i + 1:02d}',
                        calidad=['A', 'B', 'C'][i % 3],
                        estado='disponible',
                        fecha_evaluacion=timezone.now().date() - timedelta(days=2 + indice),
                    )
        
        # Etapa 7: Transferencia
        if etapa in ['transferencia', 'seguimiento']:
            from Transferencia.models import Transferencia
            from Embrion.models import Embrion
            
            embriones = Embrion.objects.filter(
                fertilizacion__ovocito__paciente=tratamiento.paciente,
                estado='disponible'
            )
            
            if embriones.exists():
                transferencia, created = Transferencia.objects.get_or_create(
                    tratamiento=tratamiento,
                    defaults={
                        'fecha': timezone.now().date() - timedelta(days=1 + indice),
                        'numero_embriones_transferidos': min(1, embriones.count()),
                        'observaciones': f'Transferencia exitosa - Embrión de calidad {embriones.first().calidad}',
                    }
                )
                
                if created:
                    # Marcar embrión como transferido
                    embrion_transferido = embriones.first()
                    embrion_transferido.estado = 'transferido'
                    embrion_transferido.save()
        
        # Etapa 8: Seguimiento post-transferencia
        if etapa == 'seguimiento':
            # Crear seguimientos adicionales
            for dias in [7, 14, 21]:
                Monitoreo.objects.get_or_create(
                    tratamiento=tratamiento,
                    fecha_atencion=timezone.now() + timedelta(days=dias),
                    defaults={
                        'descripcion': f'Seguimiento post-transferencia día +{dias}',
                        'atendido': False,
                    }
                )

    def crear_horarios_medicos(self, medicos, skip_turnos):
        """Crea horarios disponibles para todos los médicos"""
        if skip_turnos:
            self.stdout.write('⏭️ Omitiendo creación de horarios médicos...')
            return False

        self.stdout.write('\n📋 Creando horarios disponibles para médicos...')
        
        # Configuración de horarios por médico
        horarios_config = [
            {"dias": [1, 3, 5], "inicio": "09:00", "fin": "17:00"},  # Lun, Mier, Vie
            {"dias": [2, 4], "inicio": "10:00", "fin": "16:00"},     # Mar, Jue
            {"dias": [1, 2, 3, 4, 5], "inicio": "08:00", "fin": "14:00"},  # Lun-Vie
        ]
        
        exito_total = True
        for i, medico in enumerate(medicos):
            config = horarios_config[i % len(horarios_config)]
            
            self.stdout.write(f'\n  👨‍⚕️ Creando horarios para {medico.first_name} {medico.last_name}')
            
            for dia in config["dias"]:
                dias_semana = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
                
                exito = self.crear_turnos_masivos_api(
                    medico_id=medico.id,
                    dia_semana=dia,
                    hora_inicio=config["inicio"],
                    hora_fin=config["fin"]
                )
                
                if not exito:
                    exito_total = False
                    self.stdout.write(f'    ❌ Error creando horarios {dias_semana[dia]}')
                else:
                    self.stdout.write(f'    ✅ {dias_semana[dia]}: {config["inicio"]}-{config["fin"]}')
        
        if exito_total:
            self.stdout.write('\n✅ Todos los horarios médicos creados exitosamente')
        else:
            self.stdout.write('\n⚠️ Algunos horarios no se pudieron crear')
            
        return exito_total

    def sincronizar_turnos_con_api(self, turnos_locales, skip_turnos):
        """Reserva turnos específicos en la API externa usando los turnos locales"""
        if skip_turnos:
            self.stdout.write('⏭️ Omitiendo sincronización con API externa...')
            return []

        self.stdout.write('\n� Sincronizando turnos con API externa...')
        turnos_sincronizados = []
        
        for turno_data in turnos_locales:
            turno = turno_data['turno']
            tratamiento = turno_data['tratamiento']
            
            # Usar el ID real del turno local
            id_turno = turno.id
            
            turno_exitoso = self.reservar_turno_api(
                medico_id=turno.Medico.id,
                paciente_id=turno.Paciente.id,
                fecha=turno.fecha_hora.date(),
                hora=turno.fecha_hora.strftime("%H:%M"),
                id_turno=id_turno
            )
            
            if turno_exitoso:
                turnos_sincronizados.append({
                    'turno_local': turno,
                    'medico': turno.Medico,
                    'paciente': turno.Paciente,
                    'fecha': turno.fecha_hora.date()
                })
        
        self.stdout.write(f'✅ {len(turnos_sincronizados)} turnos reservados en API')
        return turnos_sincronizados

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
        
        # Datos para segundas consultas con diferentes escenarios de semen viable
        semen_viable_scenarios = [True, False, True]  # Diferentes casos para probar
        
        for i, tratamiento in enumerate(tratamientos):
            if not tratamiento.segunda_consulta:  # Solo crear si no existe
                semen_viable = semen_viable_scenarios[i % len(semen_viable_scenarios)]
                
                # Crear la segunda consulta
                segunda_consulta = SegundaConsulta.objects.create(
                    semen_viable=semen_viable,
                    ovocito_viable=True,  # Asumir que es viable por defecto
                )
                
                # Asignar la segunda consulta al tratamiento
                tratamiento.segunda_consulta = segunda_consulta
                tratamiento.save()
                
                self.stdout.write(
                    f'  ✅ Segunda consulta creada para {tratamiento.paciente.first_name} - '
                    f'Semen viable: {semen_viable}'
                )

        # =====================================
        # 5. CREAR TURNOS LOCALES
        # =====================================
        self.stdout.write('\n📅 Creando turnos locales...')
        
        from Turnos.models import Turno
        turnos_locales = []
        
        for i, tratamiento in enumerate(tratamientos):
            # Crear un turno local para cada tratamiento
            turno, created = Turno.objects.get_or_create(
                Paciente=tratamiento.paciente,
                Medico=tratamiento.medico,
                defaults={
                    'fecha_hora': timezone.now() + timedelta(days=1, hours=i+9),  # Turnos al día siguiente a las 9, 10, 11 AM
                    'cancelado': False,
                    'atendido': False,
                    'id_externo': 1000 + i,  # ID para sincronización con API
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Turno #{turno.id} creado para {tratamiento.paciente.first_name}')
            
            # Asociar el turno al tratamiento
            tratamiento.turnos.add(turno)
            self.stdout.write(f'    ✅ Turno asociado al Tratamiento #{tratamiento.id}')
            
            # Guardar para sincronizar con API externa
            turnos_locales.append({
                'turno': turno,
                'tratamiento': tratamiento
            })

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
        # 5.1 CREAR HORARIOS MÉDICOS EN API EXTERNA
        # =====================================
        horarios_creados = False
        if not options.get('skip_turnos', False):
            horarios_creados = self.crear_horarios_medicos(medicos, options.get('skip_turnos', False))

        # =====================================
        # 5.2 RESERVAR TURNOS ESPECÍFICOS EN API EXTERNA
        # =====================================
        turnos_sincronizados = []
        if not options.get('skip_turnos', False) and horarios_creados:
            turnos_sincronizados = self.sincronizar_turnos_con_api(turnos_locales, options.get('skip_turnos', False))
        elif not options.get('skip_turnos', False) and not horarios_creados:
            self.stdout.write('⚠️ No se pudieron crear horarios médicos, omitiendo reserva de turnos')

        if options.get('con_etapas', False):
            self.stdout.write('\n🔄 Aplicando etapas de tratamiento...')
            for i, tratamiento in enumerate(tratamientos):
                etapa = self.obtener_etapa_tratamiento(i)
                self.stdout.write(f'  ✅ {tratamiento.paciente.first_name} - Etapa: {etapa}')
                self.crear_datos_por_etapa(tratamiento, etapa, i)

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
        self.stdout.write(f'  🗓️  Turnos locales: {len(turnos_locales)}')
        if 'horarios_creados' in locals() and horarios_creados:
            self.stdout.write(f'  📋 Horarios médicos creados en API: ✅')
        if turnos_sincronizados:
            self.stdout.write(f'  📅 Turnos reservados en API: {len(turnos_sincronizados)}')
        
        # Mostrar etapas si se usaron
        if options.get('con_etapas', False):
            self.stdout.write(f'\n🔍 Etapas de tratamiento aplicadas:')
            for i, tratamiento in enumerate(tratamientos):
                etapa = self.obtener_etapa_tratamiento(i)
                self.stdout.write(f'  • {tratamiento.paciente.first_name}: {etapa}')
        
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
        
        # Información adicional sobre nuevas funcionalidades
        if options.get('con_etapas', False) or turnos_sincronizados or (locals().get('horarios_creados', False)):
            self.stdout.write(self.style.SUCCESS('🚀 Funcionalidades adicionales activadas:'))
            if locals().get('horarios_creados', False):
                self.stdout.write('  📋 Horarios médicos creados masivamente (5 semanas)')
            if turnos_sincronizados:
                self.stdout.write('  📅 Turnos específicos reservados con IDs sincronizados')
            if options.get('con_etapas', False):
                self.stdout.write('  🔄 Pacientes en diferentes etapas de tratamiento')
            self.stdout.write('\n  💡 Perfecto para probar "Atender Paciente"\n')