from django.contrib import admin
from .models import HistorialEmbrion


@admin.register(HistorialEmbrion)
class HistorialEmbrionAdmin(admin.ModelAdmin):
	list_display = ['id', 'embrion', 'estado', 'tipo_modificacion', 'fecha_modificacion', 'calidad']  # ✅ Corregir campos
	list_filter = ['estado', 'fecha_modificacion', 'tipo_modificacion']  # ✅ Cambiar 'fecha' por 'fecha_modificacion'
	search_fields = ['embrion__identificador', 'estado', 'observaciones']
	readonly_fields = ['fecha_modificacion']
	ordering = ['-fecha_modificacion']
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related('embrion', 'usuario')

# Register your models here.
