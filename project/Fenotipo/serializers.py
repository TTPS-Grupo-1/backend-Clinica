from rest_framework import serializers
from .models import Fenotipo


class FenotipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fenotipo
        fields = [
            "id",
            "color_ojos",
            "color_pelo",
            "tipo_pelo",
            "altura_cm",
            "complexion_corporal",
            "rasgos_etnicos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
