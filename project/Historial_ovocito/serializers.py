from rest_framework import serializers
from .models import HistorialOvocito
from django.apps import apps


class HistorialOvocitoSerializer(serializers.ModelSerializer):
    usuario_rep = serializers.StringRelatedField(source='usuario', read_only=True)
    ovocito_identificador = serializers.SerializerMethodField()

    class Meta:
        model = HistorialOvocito
        fields = ['id', 'ovocito', 'ovocito_identificador', 'paciente', 'estado', 'fecha', 'nota', 'usuario', 'usuario_rep']
        read_only_fields = ['id', 'fecha', 'usuario_rep', 'ovocito_identificador']

    def get_ovocito_identificador(self, obj):
        try:
            return obj.ovocito.identificador
        except Exception:
            return None

    def validate(self, data):
        """Validar que el ovocito pertenezca al paciente indicado.

        Si el cliente no envía `paciente`, se rellena con el paciente del ovocito.
        """
        Ovocito = apps.get_model('Ovocito', 'Ovocito')
        ovocito = data.get('ovocito')
        paciente = data.get('paciente')

        if ovocito is None:
            return data

        # si el ovocito viene y paciente no, rellenar paciente
        try:
            ovocito_obj = ovocito
            ov_paciente = getattr(ovocito_obj, 'paciente', None)
        except Exception:
            ovocito_obj = None
            ov_paciente = None

        if paciente is None and ov_paciente is not None:
            data['paciente'] = ov_paciente
            return data

        if paciente is not None and ov_paciente is not None and paciente.id != ov_paciente.id:
            raise serializers.ValidationError("El ovocito no pertenece al paciente indicado.")

        return data
