from rest_framework import serializers
from .models import Ovocito
from datetime import date
import re

class OvocitoSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Ovocito
        fields = '__all__'

        
  