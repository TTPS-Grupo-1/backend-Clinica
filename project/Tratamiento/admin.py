from django.contrib import admin
from .models import Tratamiento


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paciente', 'medico', 'fecha_inicio', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_inicio', 'fecha_creacion')
    search_fields = ('nombre', 'paciente__username', 'paciente__first_name', 'paciente__last_name', 'medico__username')
    ordering = ('-fecha_creacion',)
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Asignaciones', {
            'fields': ('paciente', 'medico')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
