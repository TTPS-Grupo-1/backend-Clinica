from rest_framework import viewsets
from ..models import Embrion
from ..serializers import EmbrionSerializer
from .create_embrion_view import CreateEmbrionMixin, UpdateEmbrionMixin

class EmbrionViewSet(CreateEmbrionMixin, UpdateEmbrionMixin, viewsets.ModelViewSet):
    queryset = Embrion.objects.all()
    serializer_class = EmbrionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Errores de validación Embrion:", serializer.errors)  # Esto lo verás en consola
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        from rest_framework import status
        from rest_framework.response import Response
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # ✅ REEMPLAZAR todo el método get_queryset por esto:
        queryset = Embrion.objects.select_related(
            'fertilizacion',
            'fertilizacion__ovocito',
            'fertilizacion__ovocito__paciente'
        ).all()
        
        paciente_id = self.request.query_params.get('paciente', None)
        
        if paciente_id:
            try:
                paciente_id = int(paciente_id)
                queryset = queryset.filter(
                    fertilizacion__isnull=False,
                    fertilizacion__ovocito__isnull=False,
                    fertilizacion__ovocito__paciente__id=paciente_id
                )
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        return queryset.distinct()    