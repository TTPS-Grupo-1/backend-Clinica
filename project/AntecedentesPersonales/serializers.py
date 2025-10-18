from rest_framework import serializers
from .models import AntecedentesPersonales


class AntecedentesPersonalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentesPersonales
        fields = [
            "id",
            "fuma_pack_dias",
            "consume_alcohol",
            "drogas_recreativas",
            "observaciones_habitos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
