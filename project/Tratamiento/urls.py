from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TratamientoViewSet

router = DefaultRouter()
router.register(r'', TratamientoViewSet, basename='tratamientos')

urlpatterns = [
    path('', include(router.urls)),
]