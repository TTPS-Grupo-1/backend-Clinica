from rest_framework import serializers
from .models import HistorialEmbrion
from django.apps import apps


class HistorialEmbrionSerializer(serializers.ModelSerializer):
    usuario_rep = serializers.StringRelatedField(source='usuario', read_only=True)
    embrion_identificador = serializers.SerializerMethodField()

    class Meta:
        model = HistorialEmbrion
        fields = ['id', 'embrion', 'embrion_identificador', 'paciente', 'estado', 'fecha', 'nota', 'usuario', 'usuario_rep']
        read_only_fields = ['id', 'fecha', 'usuario_rep', 'embrion_identificador']

    def get_embrion_identificador(self, obj):
        try:
            return obj.embrion.identificador
        except Exception:
            return None

    def validate(self, data):
        """Validar que el embrion pertenezca al paciente indicado.

        Si el cliente no envía `paciente`, se rellena con el paciente del ovocito.
        """
        Embrion = apps.get_model('Embrion', 'Embrion')
        embrion = data.get('embrion')
        paciente = data.get('paciente')

        if embrion is None:
            return data

        # si el embrion viene y paciente no, rellenar paciente
        try:
            embrion_obj = embrion
            emb_paciente = getattr(embrion_obj, 'paciente', None)
        except Exception:
            embrion_obj = None
            emb_paciente = None

        if paciente is None and emb_paciente is not None:
            data['paciente'] = emb_paciente
            return data

        if paciente is not None and emb_paciente is not None and paciente.id != emb_paciente.id:
            raise serializers.ValidationError("El embrion no pertenece al paciente indicado.")

        return data
