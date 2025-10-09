"""
ViewSet principal que combina todas las operaciones de pacientes.
Hereda de todos los mixins especializados para proporcionar funcionalidad completa.
"""

from rest_framework import viewsets
from ..models import Paciente
from ..serializers import PacienteSerializer
from .create_paciente_view import CreatePacienteMixin

import logging

logger = logging.getLogger(__name__)


class PacienteViewSet(
    CreatePacienteMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de pacientes.
    Combina todas las operaciones CRUD y funcionalidades avanzadas.
    
    Endpoints disponibles:
    - CRUD Básico:
      - GET/POST   /api/pacientes/
      - GET/PUT/PATCH/DELETE /api/pacientes/{id}/
    
    - Funcionalidades Avanzadas:
      - GET    /api/pacientes/search/?q=Juan&type=nombre
      - GET    /api/pacientes/statistics/
      - POST   /api/pacientes/bulk_delete/
    """
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    
   