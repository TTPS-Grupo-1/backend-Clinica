from rest_framework import serializers
from .models import Transferencia, TransferenciaEmbrion
from Embrion.models import Embrion
from Tratamiento.models import Tratamiento
from django.db import transaction
from Historial_embrion.models import HistorialEmbrion


class EmbrionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embrion
        fields = ('id', 'identificador', 'estado', 'calidad')


class TransferenciaEmbrionSerializer(serializers.ModelSerializer):
    embrion = serializers.PrimaryKeyRelatedField(queryset=Embrion.objects.all())

    class Meta:
        model = TransferenciaEmbrion
        fields = ('id', 'embrion', 'realizado_por', 'fecha', 'quirofano', 'test_positivo', 'observaciones', 'created_at')
        read_only_fields = ('id', 'created_at')


class TransferenciaReadSerializer(serializers.ModelSerializer):
    items = TransferenciaEmbrionSerializer(many=True, source='items_embrios', read_only=True)
    embriones = EmbrionSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Transferencia
        fields = ('id', 'tratamiento', 'realizado_por', 'fecha', 'quirofano', 'test_positivo', 'observaciones', 'created_at', 'items', 'embriones')


class TransferenciaSerializer(serializers.ModelSerializer):
    # Accept a list of embriones as input; each item may be an id or a dict
    embriones = serializers.ListField(child=serializers.JSONField(), write_only=True)

    class Meta:
        model = Transferencia
        fields = ('id', 'tratamiento', 'embriones', 'realizado_por', 'fecha', 'quirofano', 'test_positivo', 'observaciones', 'created_at')
        read_only_fields = ('created_at',)

    def validate(self, attrs):
        tratamiento = attrs.get('tratamiento')
        embriones_payload = attrs.get('embriones', [])
        if tratamiento and embriones_payload:
            paciente = tratamiento.paciente
            # normalize ids list
            ids = []
            for item in embriones_payload:
                if isinstance(item, (int, str)):
                    ids.append(int(item))
                elif isinstance(item, dict) and 'embrion' in item:
                    ids.append(int(item['embrion']))
                else:
                    raise serializers.ValidationError({'embriones': 'Lista de ids o dicts con clave "embrion" esperada.'})

            embriones_objs = Embrion.objects.filter(id__in=ids).select_related('fertilizacion__ovocito__paciente')
            if embriones_objs.count() != len(ids):
                raise serializers.ValidationError({'embriones': 'Uno o más embriones no existen.'})
            for emb in embriones_objs:
                if not getattr(emb, 'fertilizacion', None) or not getattr(emb.fertilizacion, 'ovocito', None):
                    raise serializers.ValidationError({'embriones': f'El embrión {emb.id} no tiene fertilización/ovocito asociado.'})
                emb_paciente = emb.fertilizacion.ovocito.paciente
                if emb_paciente.id != paciente.id:
                    raise serializers.ValidationError({'embriones': f'El embrión {emb.id} no pertenece a la paciente del tratamiento.'})

        return attrs

    def create(self, validated_data):
        embriones_payload = validated_data.pop('embriones', [])
        # Create the Transferencia (general data)
        transferencia = Transferencia.objects.create(**validated_data)
        created_items = []
        with transaction.atomic():
            for item in embriones_payload:
                if isinstance(item, (int, str)):
                    emb_id = int(item)
                    per = {}
                else:
                    emb_id = int(item.get('embrion'))
                    per = {k: v for k, v in item.items() if k != 'embrion'}

                embrion_obj = Embrion.objects.get(pk=emb_id)
                # Build fields for TransferenciaEmbrion
                te_data = {
                    'transferencia': transferencia,
                    'embrion': embrion_obj,
                    'realizado_por': per.get('realizado_por') or validated_data.get('realizado_por'),
                    'fecha': per.get('fecha') or validated_data.get('fecha'),
                    'quirofano': per.get('quirofano') or validated_data.get('quirofano'),
                    'test_positivo': per.get('test_positivo') if 'test_positivo' in per else validated_data.get('test_positivo', False),
                    'observaciones': per.get('observaciones') or validated_data.get('observaciones'),
                }
                item_obj = TransferenciaEmbrion.objects.create(**te_data)
                created_items.append(item_obj)

                # Registrar en historial_embrion
                HistorialEmbrion.objects.create(
                    embrion=embrion_obj,
                    paciente=transferencia.tratamiento.paciente,
                    estado='transferido',
                    calidad=str(getattr(embrion_obj, 'calidad', '') or ''),
                    nota=te_data.get('observaciones') or '',
                    observaciones=te_data.get('observaciones') or '',
                    tipo_modificacion='transferencia',
                    usuario=te_data.get('realizado_por') or validated_data.get('realizado_por')
                )

                # Marcar embrión como transferido
                # Evitar que el signal cree un historial duplicado: marcar flag temporal
                embrion_obj.estado = 'transferido'
                embrion_obj._skip_historial = True
                embrion_obj.save()

        return transferencia
