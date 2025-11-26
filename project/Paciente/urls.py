from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PacienteViewSet
from .views.deuda_paciente import DeudaPacienteView
from .views.pagar_deuda_paciente import RegistrarPagoView

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='paciente')

urlpatterns = [
    # ENDPOINT EXTRA (NO ES DEL VIEWSET)
    path("pacientes/deuda/", DeudaPacienteView.as_view(), name="deuda-paciente"),
    path("pacientes/registrar-pago/", RegistrarPagoView.as_view(), name="registrar-pago"),
]

# Agregar también las rutas generadas por el router
urlpatterns += router.urls
