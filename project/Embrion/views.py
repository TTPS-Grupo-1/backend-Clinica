from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Embrion
from .serializers import EmbrionSerializer
from .views.create_embrion_view import CreatePuncionMixin

class EmbrionViewSet(viewsets.ModelViewSet):
    serializer_class = EmbrionSerializer
    queryset = Embrion.objects.all()
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        paciente_id = self.request.query_params.get('paciente', None)
        
        if paciente_id:
            # ✅ Embrion -> Fertilizacion -> Ovocito -> Paciente
            queryset = queryset.filter(fertilizacion__ovocito__paciente__id=paciente_id)
            print(f"🔍 Buscando embriones del paciente {paciente_id}")
            print(f"📊 Encontrados: {queryset.count()} embriones")
            
            # Debug: mostrar los IDs
            for e in queryset:
                print(f"  - Embrión ID={e.id}, identificador={e.identificador}")
        
        return queryset

# Exponer las clases principales para importación externa
__all__ = [
    'EmbrionViewSet',          # ViewSet principal completo
    'CreateEmbrionMixin',      # Mixin de creación
]

EmbrionViewSet = EmbrionViewSet