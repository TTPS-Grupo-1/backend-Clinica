# Seguimiento/views.py

from rest_framework import generics
from .models import SeguimientoTratamiento
from .serializers import SeguimientoRegistroSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarSeguimientoView(generics.CreateAPIView):
    """
    POST /api/seguimiento/registrar/
    Registra el seguimiento de un tratamiento activo (encuentra el tratamiento por paciente_id).
    """
    queryset = SeguimientoTratamiento.objects.all()
    serializer_class = SeguimientoRegistroSerializer
    # No necesitamos más lógica aquí; el Serializer ya hace la búsqueda y validación.