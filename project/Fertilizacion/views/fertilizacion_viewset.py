from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..models import Fertilizacion
from ..serializers import FertilizacionSerializer
from Tratamiento.models import Tratamiento
from Fenotipo.models import Fenotipo
from django.db import transaction, IntegrityError
import logging
import requests

logger = logging.getLogger(__name__)

class FertilizacionViewSet(viewsets.ModelViewSet):
	queryset = Fertilizacion.objects.all()
	serializer_class = FertilizacionSerializer

	@action(detail=False, methods=['get'], url_path='tratamiento-info/(?P<paciente_id>[^/.]+)')
	def tratamiento_info(self, request, paciente_id=None):
		"""
		Endpoint para obtener información del tratamiento, consultas y fenotipo
		necesarios para la fertilización
		"""
		try:
			# Obtener tratamiento activo del paciente
			tratamiento = Tratamiento.objects.filter(
				paciente_id=paciente_id, 
				activo=True
			).first()
			
			if not tratamiento:
				return Response(
					{"error": "No se encontró tratamiento activo para el paciente"}, 
					status=status.HTTP_404_NOT_FOUND
				)
			
			# Obtener datos de primera consulta y fenotipo
			fenotipo_data = None
			if tratamiento.primera_consulta:
				fenotipo = Fenotipo.objects.filter(consulta=tratamiento.primera_consulta).first()
				if fenotipo:
					fenotipo_data = {
						'color_ojos': fenotipo.color_ojos,
						'color_pelo': fenotipo.color_pelo,
						'tipo_pelo': fenotipo.tipo_pelo,
						'altura_cm': fenotipo.altura_cm,
						'complexion_corporal': fenotipo.complexion_corporal,
						'rasgos_etnicos': fenotipo.rasgos_etnicos,
					}
			
			# Obtener datos de segunda consulta
			segunda_consulta_data = None
			if hasattr(tratamiento, 'segunda_consulta') and tratamiento.segunda_consulta:
				segunda_consulta_data = {
					'semen_viable': tratamiento.segunda_consulta.semen_viable,
					'ovocito_viable': tratamiento.segunda_consulta.ovocito_viable,
				}
			
			# Verificar si la paciente tiene ovocitos disponibles
			from Ovocito.models import Ovocito
			ovocitos_count = Ovocito.objects.filter(paciente_id=paciente_id).count()
			tiene_ovocitos = ovocitos_count > 0
			
			# Determinar tipo de pareja basado en el objetivo
			objetivo_lower = tratamiento.objetivo.lower() if tratamiento.objetivo else ''
			tipo_pareja = 'sin_pareja'  # default
			
			if 'embarazo gameto propio' in objetivo_lower:
				tipo_pareja = 'masculina'  # Pareja heterosexual con gametos propios
			elif 'embarazo con pareja del mismo sexo' in objetivo_lower or 'ropa' in objetivo_lower:
				tipo_pareja = 'femenina'  # Pareja femenina/lesbiana - necesita donante espermatozoide
			elif 'mujer sin pareja' in objetivo_lower or 'donante de espermatozoide' in objetivo_lower:
				tipo_pareja = 'sin_pareja'  # Mujer sola - necesita donante espermatozoide

			return Response({
				'tratamiento_id': tratamiento.id,
				'paciente': {
					'id': tratamiento.paciente.id,
					'nombre': tratamiento.paciente.first_name,
					'apellido': tratamiento.paciente.last_name,
				},
				'objetivo': tratamiento.objetivo,
				'tipo_pareja': tipo_pareja,
				'fenotipo': fenotipo_data,
				'segunda_consulta': segunda_consulta_data,
				'tiene_ovocitos': tiene_ovocitos,
				'ovocitos_count': ovocitos_count,
			})
			
		except Exception as e:
			logger.error(f"Error obteniendo información del tratamiento: {str(e)}")
			return Response(
				{"error": "Error interno del servidor"}, 
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)

	@action(detail=False, methods=['post'], url_path='buscar-banco-semen')
	def buscar_banco_semen(self, request):
		"""
		Endpoint para buscar semen compatible en el banco externo
		"""
		# El frontend envía los campos del fenotipo directamente
		fenotipo_data = request.data
		
		if not fenotipo_data:
			return Response(
				{"error": "Datos de fenotipo requeridos"}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			# Usar el proxy local para consultar la API de Supabase
			proxy_url = "http://localhost:8000/api/gametos/"
			
			# Preparar datos según el formato requerido por la API
			payload = {
				"type": "esperma",
				"phenotype": {
					"eye_color": fenotipo_data.get('color_ojos', ''),
					"hair_color": fenotipo_data.get('color_pelo', ''),
					"hair_type": fenotipo_data.get('tipo_pelo', ''),
					"height": fenotipo_data.get('altura_cm', 170),
					"complexion": fenotipo_data.get('complexion_corporal', ''),
					"ethnicity": fenotipo_data.get('rasgos_etnicos', '')
				}
			}
			logger.info(f"Payload para proxy gametos: {payload}")
			response = requests.post(proxy_url, json=payload, timeout=20)
			response.raise_for_status()

			resultados_api = response.json()

			
			# Procesar la respuesta de la API
			logger.info("Iniciando procesamiento de resultados...")
			resultados = []
			
			# La API devuelve un objeto con success, gamete, similarity
			if resultados_api.get('success') and resultados_api.get('gamete'):
				gamete = resultados_api.get('gamete', {})
				phenotypes = gamete.get('phenotypes', {})
				
				# Convertir id a string para evitar errores de subscript
				gamete_id = str(gamete.get('id', ''))
				
				# Manejar similarity de forma segura
				similarity = resultados_api.get('similarity', 0)
				if isinstance(similarity, (int, float)):
					compatibilidad = int(similarity * 100)
				else:
					compatibilidad = 0
				
				resultados.append({
					'id': gamete.get('id'),
					'identificador': f"SEM-DON-{gamete_id[:8]}",
					'compatibilidad': compatibilidad,
					'color_ojos': phenotypes.get('eye_color', ''),
					'color_pelo': phenotypes.get('hair_color', ''),
					'edad_donante': 30,  # No está en la API, usar valor por defecto
					'disponibilidad': 'alta'  # Asumimos alta si fue encontrado
				})
			else:
				logger.warning(f"No se encontró gameto compatible o respuesta errónea: {resultados_api}")
			
			return Response({
				'resultados': resultados
			})
			
		except requests.RequestException as e:
			logger.error(f"Error consultando banco de semen: {str(e)}")
			return Response(
				{"error": "Error consultando banco de semen externo"}, 
				status=status.HTTP_503_SERVICE_UNAVAILABLE
			)
		except Exception as e:
			logger.error(f"Error inesperado: {str(e)}")
			return Response(
				{"error": "Error interno del servidor"}, 
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)

	@action(detail=False, methods=['post'], url_path='buscar-banco-ovocitos')
	def buscar_banco_ovocitos(self, request):
		"""
		Endpoint para buscar ovocitos donados compatibles usando Supabase
		"""
		# El frontend envía los campos del fenotipo directamente
		fenotipo_data = request.data
		
		if not fenotipo_data:
			return Response(
				{"error": "Datos de fenotipo requeridos"}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			
			# Usar el proxy local para consultar la API de Supabase
			proxy_url = "http://localhost:8000/api/gametos/"
			
			# Preparar datos según el formato requerido por la API
			payload = {
				"type": "ovocito",  # La API usa "esperma" para ovocitos también
				"phenotype": {
					"eye_color": fenotipo_data.get('color_ojos', ''),
					"hair_color": fenotipo_data.get('color_pelo', ''),
					"hair_type": fenotipo_data.get('tipo_pelo', ''),
					"height": fenotipo_data.get('altura_cm', 170),
					"complexion": fenotipo_data.get('complexion_corporal', ''),
					"ethnicity": fenotipo_data.get('rasgos_etnicos', '')
				}
			}
			logger.info(f"Payload para proxy gametos (ovocitos): {payload}")
			
			# Realizar la petición al proxy local
			response = requests.post(proxy_url, json=payload, timeout=20)
			response.raise_for_status()
			resultados_api = response.json()
			
			# Procesar la respuesta de la API
			resultados = []
			
			# La API devuelve un objeto con success, gamete, similarity
			if resultados_api.get('success') and resultados_api.get('gamete'):
				gamete = resultados_api.get('gamete', {})
				phenotypes = gamete.get('phenotypes', {})
				
				# Convertir id a string para evitar errores de subscript
				gamete_id = str(gamete.get('id', ''))
				
				# Manejar similarity de forma segura
				similarity = resultados_api.get('similarity', 0)
				if isinstance(similarity, (int, float)):
					compatibilidad = int(similarity * 100)
				else:
					compatibilidad = 0
				
				resultados.append({
					'id': gamete.get('id'),
					'identificador': f"OVO-DON-{gamete_id[:8]}",
					'compatibilidad': compatibilidad,
					'color_ojos': phenotypes.get('eye_color', ''),
					'color_pelo': phenotypes.get('hair_color', ''),
					'edad_donante': 25,  # No está en la API, usar valor por defecto
					'cantidad_disponible': 5,  # Asumimos disponibilidad
					'estado': 'criopreservado'  # Estado por defecto
				})
			else:
				logger.warning(f"No se encontró ovocito compatible o respuesta errónea: {resultados_api}")
			
			return Response({
				'resultados': resultados
			})
			
		except requests.RequestException as e:
			logger.error(f"Error consultando banco de ovocitos: {str(e)}")
			return Response(
				{"error": "Error consultando banco de ovocitos externo"}, 
				status=status.HTTP_503_SERVICE_UNAVAILABLE
			)
		except Exception as e:
			logger.error(f"Error inesperado en banco ovocitos: {str(e)}")
			return Response(
				{"error": "Error interno del servidor"}, 
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)

	def create(self, request):
		serializer = FertilizacionSerializer(data=request.data)
		print("Creando fertilización desde ViewSet...")

		# Validación inicial
		if not serializer.is_valid():
			logger.warning(f"Errores de validación Fertilización: {serializer.errors}")
			return Response({
				"success": False,
				"message": "Hay errores en los campos de la fertilización.",
				"errors": serializer.errors
			}, status=status.HTTP_400_BAD_REQUEST)

		try:
			with transaction.atomic():
				# Guardar la fertilización
				fertilizacion = serializer.save()
				
				# ✅ Asegurar que el id existe
				fertilizacion.refresh_from_db()
				
				# Marcar ovocito como usado
				ovocito = fertilizacion.ovocito
				ovocito.usado = True
				ovocito.save(update_fields=["usado"])
				logger.info(f"Ovocito {ovocito.id_ovocito} marcado como usado")

				# Construir respuesta final
				result = {
					"success": True,
					"message": "Fertilización registrada correctamente.",
					"id": fertilizacion.id_fertilizacion,  # ✅ Agregar el id en el nivel raíz
					"data": FertilizacionSerializer(fertilizacion).data,
					"embryo": None
				}
				
				

				return Response(result, status=status.HTTP_201_CREATED)

		except IntegrityError as e:
			logger.error(f"Error de integridad al crear fertilización: {str(e)}")
			return Response({
				"success": False,
				"message": "Error de integridad al registrar la fertilización."
			}, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logger.exception("Error inesperado al crear fertilización.")
			return Response({
				"success": False,
				"message": f"Ocurrió un error al registrar la fertilización: {str(e)}"
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
