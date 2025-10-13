from rest_framework import serializers
from .models import Paciente
from datetime import date
import re
from django.contrib.auth.models import User
class PacienteSerializer(serializers.ModelSerializer):


    nombre = serializers.SerializerMethodField(read_only=True)
    apellido = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'
        extra_fields = ['nombre', 'apellido']
        extra_kwargs = {
                'email': {
                    'error_messages': {
                        'unique': "Ya existe un paciente registrado con este email."
                    }
                },
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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

