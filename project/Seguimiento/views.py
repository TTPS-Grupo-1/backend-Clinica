# Seguimiento/views.py

from rest_framework import generics
from .models import SeguimientoTratamiento
from .serializers import SeguimientoRegistroSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

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