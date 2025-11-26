from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
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

@api_view(['GET'])
def verificar_criopreservacion_previa(request, embrion_id):
    """
    Verifica si un embrión ya fue criopreservado anteriormente
    """
    try:
        # Buscar en el historial si el embrión tuvo el estado "criopreservado"
        fue_criopreservado = HistorialEmbrion.objects.filter(
            embrion_id=embrion_id,
            estado='criopreservado'
        ).exists()
        
        return Response({
            'fue_criopreservado': fue_criopreservado
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
