from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'dni',
            'telefono',
            'rol',
            'fecha_nacimiento',
            'obra_social',
            'numero_afiliado',
            'sexo',
            'firma_medico',
            'eliminado',
            'password',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'rol': {'required': True},
            'firma_medico': {'required': False, 'allow_null': True},
            'fecha_nacimiento': {'required': False, 'allow_null': True},
            'obra_social': {'required': False, 'allow_null': True},
            'numero_afiliado': {'required': False, 'allow_null': True},
            'sexo': {'required': False, 'allow_null': True},
        }

    # -----------------------------------------------------------
    # 🔹 Validaciones personalizadas
    # -----------------------------------------------------------
    def validate_fecha_nacimiento(self, value):
        """
        Valida que la fecha no sea futura y que el paciente sea mayor de edad.
        """
        if value and value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        edad = date.today().year - value.year - (
            (date.today().month, date.today().day) < (value.month, value.day)
        )
        if edad < 18:
            raise serializers.ValidationError("El usuario debe ser mayor de 18 años.")
        return value

    def validate(self, attrs):
        """
        Valida que ciertos campos estén presentes dependiendo del rol.
        """
        rol = attrs.get("rol")

        # Reglas según tipo de usuario
        if rol == "PACIENTE":
            if not attrs.get("fecha_nacimiento"):
                raise serializers.ValidationError({
                    "fecha_nacimiento": "Los pacientes deben tener fecha de nacimiento."
                })
            if not attrs.get("obra_social"):
                raise serializers.ValidationError({
                    "obra_social": "Los pacientes deben tener obra social."
                })

        if rol == "MEDICO":
            # Si querés forzar firma:
            # if not attrs.get("firma_medico"):
            #     raise serializers.ValidationError({"firma_medico": "Los médicos deben tener una firma cargada."})
            pass

        return attrs

    # -----------------------------------------------------------
    # 🔹 Creación segura de usuario
    # -----------------------------------------------------------
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    # -----------------------------------------------------------
    # 🔹 Actualización segura (sin romper password)
    # -----------------------------------------------------------
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
