from rest_framework import viewsets
from ..models import Puncion
from ..serializers import PuncionSerializer
from .create_puncion_view import CreatePuncionMixin

class PuncionViewSet(CreatePuncionMixin, viewsets.ModelViewSet):
    queryset = Puncion.objects.all()
    serializer_class = PuncionSerializer
