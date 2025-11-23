from django.urls import path
from .views import ObrasSocialesFinanzasView, PacientesFinanzasView

urlpatterns = [
    path("obras-sociales/", ObrasSocialesFinanzasView.as_view(), name="finanzas-obras"),
    path("pacientes/", PacientesFinanzasView.as_view(), name="finanzas-pacientes"),
]
