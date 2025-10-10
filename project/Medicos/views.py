from django.shortcuts import render
from .views.medico_viewset import MedicoViewSet
from .views.create_medico_view import CreateMedicoMixin

__all__ = [
    'MedicoViewSet',
    'CreateMedicoMixin'
]

MedicoViewSet = MedicoViewSet
# Create your views here.
