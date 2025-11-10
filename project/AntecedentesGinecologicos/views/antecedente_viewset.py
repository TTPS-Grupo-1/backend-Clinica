from rest_framework import viewsets
from ..models import AntecedentesGinecologicos
from ..serializers import AntecedentesGinecologicosSerializer
from .create_antecedente_view import CreateAntecedenteMixin
import logging

logger = logging.getLogger(__name__)


class AntecedentesGinecologicosViewSet(
    CreateAntecedenteMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet principal para la gestión de antecedentes ginecológicos.
    Combina mixins por operación con ModelViewSet y devuelve respuestas
    en el mismo formato que el resto de las APIs del proyecto.
    """
    queryset = AntecedentesGinecologicos.objects.all()
    serializer_class = AntecedentesGinecologicosSerializer
