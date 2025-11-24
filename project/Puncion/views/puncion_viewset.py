from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Puncion
from ..serializers import PuncionSerializer
from .create_puncion_view import CreatePuncionMixin

class PuncionViewSet(CreatePuncionMixin, viewsets.ModelViewSet):
    queryset = Puncion.objects.all()
    serializer_class = PuncionSerializer

    @action(detail=False, methods=['get'], url_path=r'existe-puncion/(?P<paciente_id>\d+)')
    def existe_puncion(self, request, paciente_id=None):
        """
        Devuelve si existe alguna punción para el paciente dado.
        GET /api/puncion/existe-puncion/{paciente_id}/
        """
        existe = Puncion.objects.filter(paciente_id=paciente_id).exists()
        return Response({'existe_puncion': existe})
