# Orden/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Orden # Asumo que tu modelo Orden está aquí
from .serializers import OrdenDescargaSerializer 
from Tratamiento.models import Tratamiento # 💡 Necesitas importar el modelo Tratamiento

class OrdenesPacienteListView(APIView):
    """
    Lista las órdenes médicas del paciente que tienen PDF disponible,
    filtrando a través de la tabla Tratamiento.
    """
    def get(self, request):
        paciente_id = request.query_params.get('paciente_id')

        if not paciente_id:
            return Response({"error": "Falta el parámetro paciente_id."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. Obtener todas las instancias de Tratamiento para este paciente
            #    (Un paciente puede tener varios tratamientos)
            tratamientos = Tratamiento.objects.filter(paciente_id=paciente_id)
            
            # 2. Extraer los IDs únicos de PrimeraConsulta vinculados a esos tratamientos
            #    Esto podría ser ineficiente, por lo que usaremos una consulta inversa (__in)
            
            # 3. La consulta de Django más eficiente (utiliza el doble guion bajo '__')
            #    Ruta de consulta: Orden -> primera_consulta -> tratamiento -> paciente
            
            ordenes = Orden.objects.filter(
                primera_consulta__tratamiento__paciente_id=paciente_id,
                pdf_url__isnull=False
            ).order_by('-fecha_creacion')
            
            # Nota: El nombre 'tratamiento_tratamiento' depende de cómo Django nombró el accesor inverso
            # desde PrimeraConsulta a Tratamiento. Si el nombre de la FK en Tratamiento es
            # 'primera_consulta', la ruta debería ser 'primera_consulta__tratamiento__paciente_id'.
            
            if not ordenes.exists():
                # Devuelve un array vacío si no hay órdenes
                return Response([], status=status.HTTP_200_OK)

            # 4. Serializar y devolver
            serializer = OrdenDescargaSerializer(ordenes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Capturar errores de DB o de ruta de FK
            print(f"Error en OrdenesPacienteListView: {e}")
            return Response({"error": "Error interno del servidor o ruta de FK inválida."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)