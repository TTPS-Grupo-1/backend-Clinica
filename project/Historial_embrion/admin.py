from django.contrib import admin
from .models import HistorialEmbrion


@admin.register(HistorialEmbrion)
class HistorialEmbrionAdmin(admin.ModelAdmin):
	list_display = ('id', 'embrion', 'paciente', 'estado', 'fecha')
	list_filter = ('estado', 'fecha')
	search_fields = ('embrion__identificador', 'paciente__email', 'estado')

# Register your models here.
