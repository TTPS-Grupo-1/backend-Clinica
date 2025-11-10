from rest_framework import serializers
from .models import Paciente
from django.contrib.auth import get_user_model

User = get_user_model()


class PacienteSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField(read_only=True)
    apellido = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'
        extra_fields = ['nombre', 'apellido']
        extra_kwargs = {
            'dni': {
                'error_messages': {
                    'unique': "Ya existe un paciente registrado con este DNI."
                }
            }
        }

    def get_nombre(self, obj):
        return obj.nombre

    def get_apellido(self, obj):
        return obj.apellido

    def validate_email(self, value):
        """
        Valida que el email no esté registrado en el modelo de usuario activo (CustomUser)
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
