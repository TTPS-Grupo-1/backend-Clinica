from django.contrib import admin
from .models import Tratamiento


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_paciente_nombre',  # ✅ Método personalizado
        'get_medico_nombre',    # ✅ Método personalizado
        'fecha_inicio',
        'activo'
    ]
    list_filter = ['activo', 'fecha_inicio']
    search_fields = [
        'paciente__first_name',
        'paciente__last_name',
        'paciente__dni',
        'medico__first_name',
        'medico__last_name',
        'medico__dni',
    ]
    readonly_fields = ['fecha_inicio']
    
    def get_paciente_nombre(self, obj):
        """Muestra el nombre completo del paciente"""
        return f"{obj.paciente.first_name} {obj.paciente.last_name} (DNI: {obj.paciente.dni})"
    get_paciente_nombre.short_description = 'Paciente'
    
    def get_medico_nombre(self, obj):
        """Muestra el nombre completo del médico"""
        return f"{obj.medico.first_name} {obj.medico.last_name}"
    get_medico_nombre.short_description = 'Médico'
