from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistorialEmbrionViewSet, verificar_criopreservacion_previa

router = DefaultRouter()
router.register(r'historial-embriones', HistorialEmbrionViewSet, basename='historial-embrion')

urlpatterns = [
    path('', include(router.urls)),
    path('historial-embrion/verificar-criopreservacion/<int:embrion_id>/',  # ✅ Agregar prefijo
         verificar_criopreservacion_previa,
         name='verificar-criopreservacion'),
]
