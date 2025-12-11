# Seguimiento/views.py

from rest_framework import generics, status
from .models import SeguimientoTratamiento
from .serializers import SeguimientoRegistroSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Tratamiento.models import Tratamiento

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarSeguimientoView(generics.CreateAPIView):
    """
    POST /api/seguimiento/registrar/
    Registra el seguimiento de un tratamiento activo (encuentra el tratamiento por paciente_id).
    """
    queryset = SeguimientoTratamiento.objects.all()
    serializer_class = SeguimientoRegistroSerializer
    # No necesitamos más lógica aquí; el Serializer ya hace la búsqueda y validación.

@api_view(['GET'])
def tiene_seguimiento(request, tratamiento_id):
    """
    Devuelve si el tratamiento tiene seguimiento asociado.
    """
    tiene = SeguimientoTratamiento.objects.filter(tratamiento_id=tratamiento_id).exists()
    return Response({'tiene_seguimiento': tiene})

class ObtenerSeguimientoView(generics.RetrieveAPIView):
    serializer_class = SeguimientoRegistroSerializer
    
    # Esta vista recibirá el ID del paciente como un query parameter (?paciente_id=X)
    def get(self, request, *args, **kwargs):
        paciente_id = request.query_params.get('paciente_id')
        
        if not paciente_id:
            return Response({"error": "Debe proporcionar el ID del paciente."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. Encontrar el Tratamiento Activo (o el más reciente)
            tratamiento = Tratamiento.objects.filter(
                paciente_id=paciente_id,
            ).order_by('-fecha_modificacion').first() 
            
            if not tratamiento:
                # Si no hay tratamiento, no hay seguimiento. Devolvemos 404 limpio.
                return Response({}, status=status.HTTP_404_NOT_FOUND)

            # 2. Intentar obtener el registro de Seguimiento (OneToOneField)
            # Asumimos related_name='seguimiento_beta'
            seguimiento = getattr(tratamiento, 'seguimiento_beta', None)
            
            if not seguimiento:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            
            # 3. Serializar y devolver los datos
            serializer = self.get_serializer(seguimiento)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)