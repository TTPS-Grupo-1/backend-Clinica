from rest_framework import routers
from .views import TransferenciaViewSet
from django.urls import path, include

router = routers.DefaultRouter()
# Los tratamientos ahora están en la app Tratamiento (/api/tratamiento/)
router.register(r'transferencias', TransferenciaViewSet, basename='transferencia')

urlpatterns = [
    path('', include(router.urls)),
]
