from rest_framework import viewsets
from ..models import Medico
from ..serializers import MedicoSerializer
from .create_medico_view import CreateMedicoMixin

import logging

logger = logging.getLogger(__name__)


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
