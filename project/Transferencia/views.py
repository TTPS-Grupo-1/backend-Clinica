from rest_framework import viewsets, permissions
from .models import Transferencia
from .serializers import TransferenciaSerializer, EmbrionSimpleSerializer, TransferenciaReadSerializer
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

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        """Accepts payload: {"tratamiento": <id>, "embriones": [{"embrion": id, "estado": ..., ...}, ...]}
        Creates multiple Transferencia rows (one per embryo) in a transaction and returns them.
        """
        tratamiento_id = request.data.get('tratamiento')
        embriones_payload = request.data.get('embriones', [])
        if not tratamiento_id or not isinstance(embriones_payload, list) or len(embriones_payload) == 0:
            return Response({'detail': 'tratamiento and embriones (non-empty list) are required.'}, status=400)

        try:
            tratamiento = Tratamiento.objects.get(pk=tratamiento_id)
        except Tratamiento.DoesNotExist:
            return Response({'detail': 'Tratamiento no encontrado.'}, status=404)

        # Permitido: el owner del tratamiento, personal o médicos (se pueden añadir checks)
        user = request.user

        # Delegate creation to the serializer which will create one Transferencia and N TransferenciaEmbrion
        data = request.data.copy()
        serializer = TransferenciaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        transferencia = serializer.save()

        out = TransferenciaReadSerializer(transferencia)
        return Response(out.data, status=201)
