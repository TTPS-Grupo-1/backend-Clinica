from rest_framework import viewsets, permissions, filters
from .models import HistorialEmbrion
from .serializers import HistorialEmbrionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class IsMedicoOrOwnerReadOnly(permissions.BasePermission):
    """Permiso sencillo: escritura sólo por médicos, operadores de laboratorio o staff; lectura por propietario o personal autorizado."""

    def has_permission(self, request, view):
        # Permitir lectura a usuarios autenticados; escritura solo a staff, MEDICO o LAB_OPERATOR
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        rol = getattr(request.user, 'rol', '')
        return getattr(request.user, 'is_staff', False) or rol in ('MEDICO', 'OPERADOR_LABORATORIO')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # permitir si es medico, operador de laboratorio o staff
            if getattr(request.user, 'rol', '') in ('MEDICO', 'OPERADOR_LABORATORIO') or request.user.is_staff:
                return True
            # si el usuario es paciente, permitir sólo si es el dueño
            return getattr(request.user, 'id', None) == getattr(obj.paciente, 'id', None)
        # escrituras ya validadas en has_permission
        return self.has_permission(request, view)


class HistorialEmbrionViewSet(viewsets.ModelViewSet):
    queryset = HistorialEmbrion.objects.select_related('embrion', 'paciente', 'usuario').all()
    serializer_class = HistorialEmbrionSerializer
    permission_classes = [IsMedicoOrOwnerReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['estado', 'nota']

    def get_queryset(self):
        qs = super().get_queryset()
        paciente = self.request.query_params.get('paciente')
        embrion = self.request.query_params.get('embrion')
        if paciente:
            qs = qs.filter(paciente_id=paciente)
        if embrion:
            qs = qs.filter(embrion_id=embrion)
        # Si el usuario es paciente, limitar a su propio paciente id
        if getattr(self.request.user, 'rol', '') == 'PACIENTE':
            qs = qs.filter(paciente_id=self.request.user.id)
        return qs

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=False, methods=["get"], url_path=r"por-embrion/(?P<embrion_id>[^/.]+)")
    def por_embrion(self, request, embrion_id=None):
        """Lista los historiales filtrados por el id de embrion pasado en la URL.

        Ruta resultante: /api/historial_embrion/por-embrion/<embrion_id>/
        Esto es útil cuando querés pasar el id como parte del path en vez de query-string.
        """
        qs = self.filter_queryset(self.get_queryset().filter(embrion_id=embrion_id))
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
from django.shortcuts import render

# Create your views here.
