from rest_framework import serializers
from .models import Transferencia
from Embrion.models import Embrion
from Tratamiento.models import Tratamiento


class EmbrionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embrion
        fields = ('id', 'identificador', 'estado', 'calidad')


# El TratamientoSerializer ahora está en Tratamiento.serializers
# from Tratamiento.serializers import TratamientoSerializer


class TransferenciaSerializer(serializers.ModelSerializer):
    embriones = serializers.PrimaryKeyRelatedField(queryset=Embrion.objects.all(), many=True)

    class Meta:
        model = Transferencia
        fields = ('id', 'tratamiento', 'embriones', 'fecha', 'causa', 'nacido_vivo', 'test_positivo', 'observaciones', 'created_at')
        read_only_fields = ('created_at',)

    def validate(self, attrs):
        # Validate that selected embriones belong to the paciente of the tratamiento
        tratamiento = attrs.get('tratamiento')
        embriones = attrs.get('embriones', [])
        if tratamiento:
            paciente = tratamiento.paciente
            invalid = []
            for emb in embriones:
                # Navigate Embrión -> Fertilizacion -> Ovocito -> paciente
                if not emb.fertilizacion or not emb.fertilizacion.ovocito:
                    invalid.append(emb.identificador)
                else:
                    emb_paciente = emb.fertilizacion.ovocito.paciente
                    if emb_paciente.id != paciente.id:
                        invalid.append(emb.identificador)
            if invalid:
                raise serializers.ValidationError({'embriones': f"Los siguientes embriones no pertenecen a la paciente del tratamiento: {', '.join(invalid)}"})
        return attrs

    def create(self, validated_data):
        embriones = validated_data.pop('embriones', [])
        transferencia = Transferencia.objects.create(**validated_data)
        transferencia.embriones.set(embriones)
        return transferencia
