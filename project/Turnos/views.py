# app/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..models import Turno
from ..serializers import TurnoSerializer

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        id_externo = self.request.query_params.get('id_externo', None)
        
        if id_externo:
            queryset = queryset.filter(id_externo=id_externo)
        
        return queryset

    
