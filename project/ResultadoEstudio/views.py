from collections import defaultdict
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ResultadoEstudio
from .serializers import ResultadoEstudioSerializer


class ResultadoEstudioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar los resultados de estudios.
    """
    queryset = ResultadoEstudio.objects.all()
    serializer_class = ResultadoEstudioSerializer

    @action(detail=False, methods=['get'], url_path=r'agrupados-por-consulta/(?P<consulta_id>\d+)')
    def agrupados_por_consulta(self, request, consulta_id=None):
        """
        Endpoint: /api/resultado_estudio/agrupados-por-consulta/<consulta_id>/
        Devuelve los estudios agrupados por persona y tipo.
        """
        try:
            estudios = ResultadoEstudio.objects.filter(consulta_id=consulta_id)
            agrupado = defaultdict(lambda: defaultdict(list))

            for e in estudios:
                persona = getattr(e, "persona", "PACIENTE")  # campo opcional
                tipo = e.tipo_estudio or "Sin tipo"
                agrupado[persona][tipo].append({
                    "id": e.id,
                    "nombre_estudio": e.nombre_estudio,
                    "valor": e.valor,
                })

            resultado = []
            for persona, tipos in agrupado.items():
                resultado.append({
                    "persona": persona,
                    "tipos_estudios": [
                        {"tipo": tipo, "estudios": lista_estudios}
                        for tipo, lista_estudios in tipos.items()
                    ]
                })

            return Response(
                {"consulta_id": consulta_id, "estudios": resultado},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
