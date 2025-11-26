from django.contrib import admin
from .models import Transferencia, TransferenciaEmbrion

# El TratamientoAdmin ahora está en Tratamiento/admin.py


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tratamiento', 'embryos_display', 'realizado_por', 'fecha')
    list_filter = ('test_positivo',)
    search_fields = ('tratamiento__nombre', 'tratamiento__paciente__first_name', 'embriones__identificador')
    # No incluir la M2M 'embriones' en fieldsets porque especifica un modelo
    # intermedio (through). En su lugar, registramos un inline para editar
    # los items de `TransferenciaEmbrion`.
    inlines = []

    fieldsets = (
        ('Información General', {
            'fields': ('tratamiento', 'realizado_por', 'fecha', 'quirofano')
        }),
        ('Resultados y Observaciones', {
            'fields': ('test_positivo', 'observaciones')
        }),
    )

    # registraremos el inline abajo después de su declaración

    def embryos_display(self, obj):
        # Mostrar hasta 5 identificadores de embriones asociados
        try:
            ids = [e.identificador for e in obj.embriones.all()[:5]]
            more = obj.embriones.count() - len(ids)
            s = ', '.join(ids)
            if more > 0:
                s = f"{s} (+{more} más)"
            return s or '(sin embriones)'
        except Exception:
            return '(error)'

    embryos_display.short_description = 'Embriones'


class TransferenciaEmbrionInline(admin.TabularInline):
    model = TransferenciaEmbrion
    extra = 0
    raw_id_fields = ('embrion', 'realizado_por')
    fields = ('embrion', 'realizado_por', 'fecha', 'quirofano', 'test_positivo', 'observaciones')


# Attach the inline to the admin class
TransferenciaAdmin.inlines = [TransferenciaEmbrionInline]
