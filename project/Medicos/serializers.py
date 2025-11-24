from rest_framework import serializers
from .models import Medico
from django.contrib.auth.hashers import make_password

class MedicoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=False,
        min_length=8,
        allow_blank=False
    )

    
    
    
    class Meta:
        model = Medico
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'dni': {'read_only': True}
        }
    
    def validate(self, attrs):
        """
        Validación personalizada según si es creación o actualización
        """
        # Si es creación (no hay instance), password es obligatorio
        if not self.instance and 'password' not in attrs:
            raise serializers.ValidationError({
                'password': 'La contraseña es requerida al crear un médico'
            })
        
        if not self.instance and attrs.get('password', '').strip() == '':
            raise serializers.ValidationError({
                'password': 'La contraseña no puede estar vacía'
            })
        
        return attrs
    
    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # No permitir actualizar contraseña desde aquí
        validated_data.pop('password', None)
        
        # 👇 ESTO ES LO IMPORTANTE: Permitir actualizar eliminado
        return super().update(instance, validated_data)