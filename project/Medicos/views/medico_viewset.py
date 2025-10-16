from rest_framework import viewsets
from Medicos.models import Medico
from Medicos.serializers import MedicoSerializer
from .create_medico_view import CreateMedicoMixin

class MedicoViewSet(
    CreateMedicoMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de médicos.
    Combina mixin de creación y CRUD estándar.
    """
    serializer_class = MedicoSerializer
    lookup_field = 'dni'
    
    def get_queryset(self):
        """
        Por defecto, solo devuelve médicos no eliminados
        """
        queryset = Medico.objects.all()
        
        # Filtrar médicos no eliminados (a menos que se pida explícitamente)
        if self.request.query_params.get('incluir_eliminados') != 'true':
            queryset = queryset.filter(eliminado=False)
        
        return queryset.order_by('apellido', 'nombre')
