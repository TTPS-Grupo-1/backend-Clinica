from rest_framework import viewsets, status
from rest_framework.decorators import action
from Turnos.models import Turno
from rest_framework.response import Response
from Turnos.serializers import TurnoSerializer
from Turnos.views.create_turno_view import CreateTurnoMixin
import requests
from django.http import JsonResponse
class TurnoViewSet(CreateTurnoMixin, viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer  

    @action(detail=False, methods=["get"], url_path="medico/(?P<id_medico>[^/.]+)")
    def get_turnos_medico_proxy(self, request, id_medico: int):
        print(f"📩 Consultando turnos para el médico con ID: {id_medico}")
        SUPABASE_EDGE_URL = "https://ahlnfxipnieoihruewaj.supabase.co/functions/v1/get_turnos_medico"
        SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9ncnVwbyI6MSwiaWF0IjoxNzYwNzI0ODEzfQ.9SeVdilNSRro5wivM50crPF-B1Mn1KB_2z65PXF1hbc" 
        try:
            url = f"{SUPABASE_EDGE_URL}?id_medico={id_medico}"
            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            }
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            print(f"✅ Respuesta recibida: {resp.json()}")
            return JsonResponse(resp.json(), safe=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar turnos: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
            return JsonResponse({"error": str(e)}, status=500)
    @action(detail=False, methods=['get'], url_path='por-id-externo/(?P<id_externo>[^/.]+)')
    def por_id_externo(self, request, id_externo=None):
        """
        Endpoint para obtener un turno por su id_externo.
        GET /api/turnos/por-id-externo/<id_externo>/
        """
        print(f"🔍 Buscando turno con id_externo: {id_externo}")  # ✅ Log
        print(f"🔍 Tipo de id_externo: {type(id_externo)}")  # ✅ Log
        
        try:
            # Convertir a int si es necesario
            id_externo_int = int(id_externo)
            print(f"🔍 id_externo convertido a int: {id_externo_int}")  # ✅ Log
            
            turno = Turno.objects.get(id_externo=id_externo_int)
            print(f"✅ Turno encontrado: {turno}")  # ✅ Log
            
            serializer = self.get_serializer(turno)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Turno.DoesNotExist:
            print(f"❌ No se encontró turno con id_externo {id_externo}")  # ✅ Log
            return Response(
                {"detail": f"No se encontró un turno con id_externo {id_externo}."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            print(f"❌ Error de conversión: {e}")  # ✅ Log
            return requests.Response(
                {"detail": f"id_externo inválido: {id_externo}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")  # ✅ Log
            return Response(
                {"detail": f"Error al buscar turno: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='por-externos')
    def por_externos(self, request):
        """
        Endpoint para obtener los turnos locales cuyo `id_externo` esté en la lista provista.
        GET /api/local/turnos/por-externos/?ids=1,2,3&atendido=false
        Parámetros:
          - ids: lista separada por comas de id_externo (requerido para filtrar)
          - atendido: 'true'|'false' (opcional) para filtrar por estado de atención
        """
        ids_param = request.query_params.get('ids')
        atendido_param = request.query_params.get('atendido')
        try:
            qs = Turno.objects.all()
            if ids_param:
                # parsear lista de ids
                try:
                    ids_list = [int(x) for x in ids_param.split(',') if x.strip()]
                except ValueError:
                    return Response({'detail': 'ids debe ser una lista de enteros separados por comas.'}, status=status.HTTP_400_BAD_REQUEST)
                qs = qs.filter(id_externo__in=ids_list)

            if atendido_param is not None:
                ap = atendido_param.lower()
                if ap in ('true', '1'):
                    qs = qs.filter(atendido=True)
                elif ap in ('false', '0'):
                    qs = qs.filter(atendido=False)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ Error al filtrar turnos locales por externos: {e}")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='marcar-atendido')
    def marcar_atendido(self, request, pk=None):
        """Marca un turno local como atendido: POST /api/local/turnos/{pk}/marcar-atendido/"""
        try:
            turno = self.get_object()
            turno.atendido = True
            turno.save()
            serializer = self.get_serializer(turno)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ Error marcando turno como atendido: {e}")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='tiene-turnos-pendientes/(?P<id_medico>\d+)')
    def tiene_turnos_pendientes(self, request, id_medico=None):
        """
        Devuelve si el médico tiene al menos un turno pendiente (atendido=False).
        GET /api/turnos/tiene-turnos-pendientes/<id_medico>/
        """
        existe = Turno.objects.filter(Medico_id=id_medico, atendido=False).exists()
        return Response({'tiene_turnos_pendientes': existe})
