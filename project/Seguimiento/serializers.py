# Seguimiento/serializers.py

from rest_framework import serializers
from django.db import transaction

from Transferencia.models import Transferencia
from .models import SeguimientoTratamiento
from Tratamiento.models import Tratamiento 
from django.utils import timezone 

class SeguimientoRegistroSerializer(serializers.ModelSerializer):
    paciente_id = serializers.IntegerField(write_only=True)

    # 1. Declaración explícita de campos que necesitan manejo especial de NULL/Blank
    # Esto soluciona el error 400 de formato de fecha.
    fecha_nacimiento = serializers.DateField(
        required=False,
        allow_null=True, 
        input_formats=['%Y-%m-%d'],
    )
    
    causa = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    
    # id_transferencia es ForeignKey, DRF lo infiere, pero si lo declaras, debes manejarlo.
    # Si no lo declaraste explícitamente en el código original, lo dejamos sin declarar
    # y confiamos en la limpieza de to_internal_value. Si lo hiciste:
    # id_transferencia = serializers.PrimaryKeyRelatedField(
    #      queryset=Transferencia.objects.all(), required=False, allow_null=True
    # )

    class Meta:
        model = SeguimientoTratamiento
        fields = [
            'paciente_id',
            'resultado_beta',
            'hay_saco_gestacional',
            'embarazo_clinico',
            'nacido_vivo',
            'causa',
            'cantidad_nacimientos',
            'id_transferencia', # Si no se declaró arriba, DRF lo infiere del modelo
            'fecha_nacimiento',
        ]
        
        # Extra_kwargs para los campos que no declaramos explícitamente (o para reforzar required=False)
        extra_kwargs = {
            'nacido_vivo': {'required': False},
            # No se necesita para 'causa' y 'fecha_nacimiento' ya que fueron declarados arriba.
            'cantidad_nacimientos': {'required': False},
            'id_transferencia': {'required': False},
            'resultado_beta': {'required': False},
            'hay_saco_gestacional': {'required': False},
            'embarazo_clinico': {'required': False},
        }

    # ✅ CORRECCIÓN CLAVE: Interceptar la data cruda y limpiarla para evitar fallos de formato 400
    def to_internal_value(self, data):
        # Creamos una copia mutable de la data cruda
        mutable_data = data.copy()

        # 1. Limpiar campos de fecha, texto y numéricos: Convertir "" y 0 a None
        campos_a_limpiar_nulo = ['fecha_nacimiento', 'causa', 'id_transferencia', 'cantidad_nacimientos']
        
        for campo in campos_a_limpiar_nulo:
            valor = mutable_data.get(campo)
            
            # Si el valor es cadena vacía o 0 (para opcionales numéricos), lo forzamos a None.
            if valor == "" or (isinstance(valor, int) and valor == 0 and campo in ['id_transferencia', 'cantidad_nacimientos']):
                mutable_data[campo] = None
        
        # 2. Llamar al super() con la data limpia
        # Si la data está limpia, super().to_internal_value() debería funcionar sin el error 400.
        try:
            # Usamos la data limpia (mutable_data) para la validación interna
            return super().to_internal_value(mutable_data)
        except serializers.ValidationError:
            # Si hay errores de validación internos (p. ej., formato de fecha incorrecto a pesar de la limpieza, o FK inválida)
            raise
    
    # ✅ LÓGICA DE NEGOCIO Y CONTROL DE ESTADO
    def validate(self, data):
        paciente_id = data.get('paciente_id')

        # 🎯 PASO 2: VALIDACIÓN DE NEGOCIO Y BÚSQUEDA DE TRATAMIENTO
        try:
            # 1. Buscar el tratamiento activo por paciente ID
            tratamiento_activo = Tratamiento.objects.filter(
                paciente_id=paciente_id,
            ).order_by('-fecha_modificacion').first() 
            
            if not tratamiento_activo:
                raise serializers.ValidationError({"paciente_id": "No se encontró un tratamiento activo para este paciente."})

            # 2. Verificar estado de seguimiento anterior (Lógica de OneToOneField)
            try:
                seguimiento_existente = getattr(tratamiento_activo, 'seguimiento_beta')
            except SeguimientoTratamiento.DoesNotExist:
                seguimiento_existente = None

            if seguimiento_existente:
                # Si ya existe, verificamos si está finalizado (nacido_vivo NO es None)
                if seguimiento_existente.nacido_vivo is not None:
                    raise serializers.ValidationError({
                        "tratamiento": f"El seguimiento del tratamiento ID {tratamiento_activo.id} ya tiene un resultado final ('Nacido Vivo' definido)."
                    })
            
            data['tratamiento'] = tratamiento_activo

        except serializers.ValidationError:
            raise
        except Exception as e:
            print(f"Error al verificar tratamiento: {e}")
            raise serializers.ValidationError({"general": "Error interno al procesar el tratamiento."})

        transferencia = (
            Transferencia.objects
            .filter(tratamiento=tratamiento_activo)
            .order_by('-created_at')
            .first()
        )

        data['id_transferencia'] = transferencia
            
        return data
        
    
    def _generar_motivo_finalizacion(self, data, tratamiento):
        """Determina el motivo finalizador si se define el resultado nacido_vivo."""
        
        nacido_vivo_status = data.get('nacido_vivo')
        
        if nacido_vivo_status is True:
            return f"Finalizado con éxito: Nacimiento(s) vivo(s) registrado(s)."
        
        if nacido_vivo_status is False:
            causa = data.get('causa') or "No especificada."
            return f"Finalizado sin nacimiento vivo. Causa: {causa[:50]}"
        
        return None # Seguimiento no finalizado

    
    def create(self, validated_data):
        """Intenta actualizar el registro existente (si existe la relación OneToOne) o lo crea."""
        
        tratamiento = validated_data.pop('tratamiento')
        validated_data.pop('paciente_id')
        
        # Mantenemos try/except para manejar la inexistencia de la relación
        try:
            seguimiento_existente = getattr(tratamiento, 'seguimiento_beta', None)
        except SeguimientoTratamiento.DoesNotExist:
            seguimiento_existente = None
        except Exception:
            seguimiento_existente = None


        if seguimiento_existente:
            # --- ACTUALIZACIÓN ---
            instance = seguimiento_existente
            
            for attr, value in validated_data.items():
                 # ⚠️ Solo actualiza si el valor no es None (para evitar borrar valores anteriores)
                 # Ya que el frontend envía todos los campos, no necesitamos esta lógica compleja
                 # y simplemente actualizamos con los valores limpios (incluyendo None si se borró el campo)
                 setattr(instance, attr, value)
            
            instance.fecha_seguimiento = timezone.now().date() 
            instance.save()
            seguimiento = instance
            
        else:
            # --- CREACIÓN ---
            seguimiento = SeguimientoTratamiento.objects.create(
                **validated_data,
                tratamiento=tratamiento
            )

        # --- Lógica de FINALIZACIÓN del Tratamiento ---
        motivo = self._generar_motivo_finalizacion(validated_data, tratamiento)

        if motivo:
            tratamiento.activo = False
            tratamiento.motivo_finalizacion = motivo
            tratamiento.save(update_fields=['activo', 'motivo_finalizacion'])

        return seguimiento