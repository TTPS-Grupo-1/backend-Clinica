"""
ViewSet principal que combina todas las operaciones de ovocitos.
Hereda de todos los mixins especializados para proporcionar funcionalidad completa.
"""

from rest_framework import viewsets
from ..models import Ovocito
from ..serializers import OvocitoSerializer
from .create_ovocito_view import CreateOvocitoMixin

import logging

logger = logging.getLogger(__name__)


class OvocitoViewSet(
    CreateOvocitoMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de ovocitos.
    Combina todas las operaciones de altas y funcionalidades avanzadas.

    Endpoints disponibles:
    - CRUD Básico:
      - GET/POST   /api/ovocitos/

    - Funcionalidades Avanzadas:
      - GET    /api/ovocitos/search/?q=Ovocito&type=identificador
      - GET    /api/ovocitos/statistics/
      - POST   /api/ovocitos/bulk_delete/
    """
    queryset = Ovocito.objects.all()
    serializer_class = OvocitoSerializer