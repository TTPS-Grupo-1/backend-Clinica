# Orden/urls.py

from django.urls import path
from .views import OrdenesPacienteListView

urlpatterns = [
    # ... otras URLs ...
    
    # ✅ Nuevo endpoint
    path('mis_ordenes/', OrdenesPacienteListView.as_view(), name='ordenes_paciente_list'),
]