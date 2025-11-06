from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..models import Fertilizacion
from ..serializers import FertilizacionSerializer
from Tratamiento.models import Tratamiento
from Fenotipo.models import Fenotipo
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
		fenotipo_data = request.data.get('fenotipo')
		
		if not fenotipo_data:
			return Response(
				{"error": "Datos de fenotipo requeridos"}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			# URL de la API externa del banco de semen (ajustar según la API real)
			banco_api_url = "https://api-banco-semen.ejemplo.com/buscar-compatibles"
			
			# Preparar datos para la API externa
			payload = {
				'color_ojos': fenotipo_data.get('color_ojos'),
				'color_pelo': fenotipo_data.get('color_pelo'),
				'tipo_pelo': fenotipo_data.get('tipo_pelo'),
				'altura_cm': fenotipo_data.get('altura_cm'),
				'complexion_corporal': fenotipo_data.get('complexion_corporal'),
				'rasgos_etnicos': fenotipo_data.get('rasgos_etnicos'),
			}
			
			# Por ahora, simulamos la respuesta ya que no tenemos la API real
			# En producción, descomenta las siguientes líneas:
			# response = requests.post(banco_api_url, json=payload, timeout=10)
			# response.raise_for_status()
			# resultados = response.json()
			
			# Respuesta simulada para desarrollo
			resultados = [
				{
					'id': 1,
					'identificador': 'SEM-001',
					'compatibilidad': 95,
					'color_ojos': fenotipo_data.get('color_ojos', 'marrón'),
					'color_pelo': fenotipo_data.get('color_pelo', 'castaño'),
				},
				{
					'id': 2,
					'identificador': 'SEM-002',
					'compatibilidad': 87,
					'color_ojos': fenotipo_data.get('color_ojos', 'marrón'),
					'color_pelo': fenotipo_data.get('color_pelo', 'negro'),
				}
			]
			
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

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			logger.warning(f"Errores de validación Fertilización: {serializer.errors}")
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
