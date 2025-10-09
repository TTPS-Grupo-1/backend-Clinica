from rest_framework import serializers
from .models import Paciente
from datetime import date
import re

class PacienteSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Paciente
        fields = '__all__'
        
  