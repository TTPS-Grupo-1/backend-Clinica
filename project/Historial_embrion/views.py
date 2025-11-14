from rest_framework import viewsets, permissions, filters
from .models import HistorialEmbrion
from .serializers import HistorialEmbrionSerializer


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


class HistorialEmbrionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialEmbrionSerializer
    queryset = HistorialEmbrion.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        embrion_id = self.request.query_params.get('embrion', None)

        if embrion_id:
            queryset = queryset.filter(embrion=embrion_id)

        return queryset
