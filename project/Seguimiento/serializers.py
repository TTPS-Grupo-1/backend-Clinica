# Seguimiento/serializers.py

from rest_framework import serializers
from .models import SeguimientoTratamiento
from Tratamiento.models import Tratamiento 

class SeguimientoRegistroSerializer(serializers.ModelSerializer):
    # 💡 Campo extra para recibir el ID del paciente, pero no mapea a un campo del modelo
    paciente_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SeguimientoTratamiento
        # ⚠️ Excluimos 'tratamiento' aquí porque lo vamos a asignar manualmente en la View
        fields = [
            'paciente_id',          # Campo de entrada (para buscar el Tratamiento)
            'resultado_beta',
            'hay_saco_gestacional',
            'embarazo_clinico',
            'nacido_vivo',
        ]
        
    def validate(self, data):
        # 💡 La validación principal: Asegurar que el tratamiento exista y sea único
        paciente_id = data.get('paciente_id')
        
        try:
            # 1. Buscar el tratamiento activo por paciente ID
            # Asumimos que quieres el tratamiento más reciente o activo.
            tratamiento_activo = Tratamiento.objects.filter(
                paciente_id=paciente_id,
                # Puedes añadir un filtro activo=True si existe en tu modelo Tratamiento
            ).order_by('-fecha_modificacion').first() 
            
            if not tratamiento_activo:
                raise serializers.ValidationError("No se encontró un tratamiento activo para este paciente.")

            # 2. Verificar si ya existe un seguimiento (por ser OneToOneField)
            if hasattr(tratamiento_activo, 'seguimiento_beta'):
                raise serializers.ValidationError(
                    f"Ya existe un registro de seguimiento para el tratamiento ID {tratamiento_activo.id}."
                )
                
            # Guardamos la instancia del tratamiento en los datos validados para usarla en create()
            data['tratamiento'] = tratamiento_activo
            
        except Exception:
            raise serializers.ValidationError("Error interno al verificar el tratamiento.")
            
        return data
    
    def _generar_motivo_finalizacion(self, data):
        if data.get('nacido_vivo'):
            return "Nacido vivo registrado"

        if data.get('embarazo_clinico'):
            return "Embarazo clínico confirmado"

        if data.get('hay_saco_gestacional'):
            return "Saco gestacional detectado"

        beta = data.get('resultado_beta')
        
        if beta is not None:
            if beta > 5:
                return f"Beta positiva ({beta} mUI/mL)"
            else:
                return f"Beta negativa ({beta} mUI/mL)"

        return "Seguimiento finalizado sin resultados concluyentes"


    def create(self, validated_data):
        # 1. Eliminar campo que no pertenece al modelo
        validated_data.pop('paciente_id')

        # 2. Recuperar tratamiento pasado desde validate()
        tratamiento = validated_data.pop('tratamiento')

        # 3. Crear seguimiento asociado
        seguimiento = SeguimientoTratamiento.objects.create(
            **validated_data,
            tratamiento=tratamiento
        )

        # 4. Generar motivo de finalización automáticamente
        motivo = self._generar_motivo_finalizacion(validated_data)

        # 5. Marcar tratamiento como inactivo y guardar motivo
        tratamiento.activo = False
        tratamiento.motivo_finalizacion = motivo
        tratamiento.save(update_fields=['activo', 'motivo_finalizacion'])

        return seguimiento
