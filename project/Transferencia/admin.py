from django.contrib import admin
from .models import Transferencia

# El TratamientoAdmin ahora está en Tratamiento/admin.py

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tratamiento', 'test_positivo', 'created_at')
    list_filter = ('test_positivo',)
    filter_horizontal = ('embriones',)
    search_fields = ('tratamiento__nombre', 'tratamiento__paciente__username')
    
    fieldsets = (
        ('Información General', {
            'fields': ('tratamiento', 'embriones')
        }),
        ('Resultados', {
            'fields': ('test_positivo',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
