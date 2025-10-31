from rest_framework import viewsets, permissions
from .models import Transferencia
from .serializers import TransferenciaSerializer, EmbrionSimpleSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from Embrion.models import Embrion
from Tratamiento.models import Tratamiento
from Tratamiento.serializers import TratamientoSerializer


# El TratamientoViewSet ahora está en la app Tratamiento


class TransferenciaViewSet(viewsets.ModelViewSet):
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset
        # Si paciente, devolver transferencias asociadas a sus tratamientos
        if user and hasattr(user, 'rol') and user.rol == 'PACIENTE':
            return qs.filter(tratamiento__paciente=user)
        return qs

    @action(detail=False, methods=['get'], url_path='embriones-paciente')
    def embriones_paciente(self, request):
        """Devuelve la lista de embriones asociados a la paciente (según tratamientos/ovocitos)."""
        paciente = request.user
        if not paciente:
            return Response({'detail': 'Autenticación requerida.'}, status=401)
        embriones = Embrion.objects.filter(fertilizacion__ovocito__paciente=paciente)
        serializer = EmbrionSimpleSerializer(embriones, many=True)
        return Response(serializer.data)
