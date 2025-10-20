from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import logging
from CustomUser.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pacientes usando CustomUser.
    Rol forzado: PACIENTE
    """
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

    # --------------------------------------------------------
    # 🔹 Filtrar solo usuarios con rol PACIENTE
    # --------------------------------------------------------
    def get_queryset(self):
        queryset = User.objects.filter(rol='PACIENTE')
        if self.request.query_params.get('incluir_eliminados') != 'true':
            queryset = queryset.filter(eliminado=False)
        return queryset.order_by('last_name', 'first_name')

    # --------------------------------------------------------
    # 🔹 Crear paciente con validaciones
    # --------------------------------------------------------
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        password = data.get("password")

        # Validar que haya password
        if not password:
            return Response(
                {"success": False, "message": "El campo 'password' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.warning(f"❌ Errores de validación: {serializer.errors}")
            return Response(
                {
                    "success": False,
                    "message": "Hay errores en los datos ingresados.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Crear usuario CustomUser (usa create_user para hashear la password)
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                password=password,
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                dni=serializer.validated_data.get("dni"),
                telefono=serializer.validated_data.get("telefono", ""),
                rol="PACIENTE",
                numero_afiliado=serializer.validated_data.get("numero_afiliado"),
                obra_social=serializer.validated_data.get("obra_social"),
                fecha_nacimiento=serializer.validated_data.get("fecha_nacimiento"),
                sexo=serializer.validated_data.get("sexo"),
                
            )

            logger.info(f"🧍 Paciente creado correctamente: {user.email}")
            return Response(
                {
                    "success": True,
                    "message": "Paciente registrado correctamente.",
                    "data": CustomUserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.exception("⚠️ Error inesperado al crear paciente")
            return Response(
                {
                    "success": False,
                    "message": f"Error al registrar paciente: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # --------------------------------------------------------
    # 🔹 Eliminado lógico
    # --------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.eliminado = True
        instance.save()
        logger.info(f"🗑️ Paciente eliminado: {instance.email} ({instance.dni})")
        return Response(
            {"success": True, "message": "Paciente eliminado correctamente."},
            status=status.HTTP_200_OK,
        )
