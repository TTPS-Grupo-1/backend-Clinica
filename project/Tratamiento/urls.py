from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TratamientoViewSet

router = SimpleRouter()
router.register(r'', TratamientoViewSet, basename='tratamientos')

urlpatterns = [
    path('', include(router.urls)),
]