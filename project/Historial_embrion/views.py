from rest_framework import viewsets
from .models import HistorialEmbrion
from .serializers import HistorialEmbrionSerializer

class HistorialEmbrionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialEmbrionSerializer

    def get_queryset(self):
        queryset = HistorialEmbrion.objects.all()
        embrion_id = self.request.query_params.get('embrion')
        if embrion_id:
            queryset = queryset.filter(embrion_id=embrion_id)
        return queryset.order_by('-fecha_modificacion')
