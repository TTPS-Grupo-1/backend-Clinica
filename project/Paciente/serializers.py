from rest_framework import serializers
from .models import Paciente
from datetime import date
import re

class PacienteSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Paciente
        fields = '__all__'
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
        
    