# Seguimiento/urls.py

from django.urls import path
from .views import RegistrarSeguimientoView

urlpatterns = [
    # Mapeo exacto de la URL de tu frontend
    path('registrar/', RegistrarSeguimientoView.as_view(), name='registrar_seguimiento'),
]

# ⚠️ Asegúrate de que esta URLconf se incluya en tu project/urls.py bajo 'api/'
# path('api/seguimiento/', include('Seguimiento.urls')),