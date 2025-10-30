from rest_framework import viewsets
from ..models import Monitoreo
from ..serializers import MonitoreoSerializer
from .create_monitoreo_view import CreateMonitoreoMixin

import logging

logger = logging.getLogger(__name__)


class MonitoreoViewSet(
    CreateMonitoreoMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de monitoreos.
    Combina mixin de creación y CRUD estándar.
    """
    queryset = Monitoreo.objects.all()
    serializer_class = MonitoreoSerializer
