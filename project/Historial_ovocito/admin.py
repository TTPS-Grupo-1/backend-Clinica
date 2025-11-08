from django.contrib import admin
from .models import HistorialOvocito


@admin.register(HistorialOvocito)
class HistorialOvocitoAdmin(admin.ModelAdmin):
	list_display = ('id', 'ovocito', 'paciente', 'estado', 'fecha')
	list_filter = ('estado', 'fecha')
	search_fields = ('ovocito__identificador', 'paciente__email', 'estado')

