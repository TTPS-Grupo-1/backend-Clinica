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
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    lookup_field = 'dni'  # 👈 Usa DNI en lugar de pk
