from rest_framework import viewsets
from Turnos.models import Turno
from Turnos.serializers import TurnoSerializer
from Turnos.views.create_turno_view import CreateTurnoMixin

class TurnoViewSet(CreateTurnoMixin, viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer