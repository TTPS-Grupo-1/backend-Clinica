from rest_framework import status
from rest_framework.response import Response
import logging
import requests
from ..models import Ovocito
from Historial_ovocito.models import HistorialOvocito

logger = logging.getLogger(__name__)


class UpdateOvocitoMixin:
    """
    Mixin para manejar la actualización de ovocitos con lógica de criopreservación.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Guardar estado anterior
        estado_anterior = instance.tipo_estado
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            logger.warning(f"Errores de validación en update: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Hay errores en los campos ingresados.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Guardar cambios
            ovocito = serializer.save()
            estado_nuevo = ovocito.tipo_estado
            
            # Detectar cambio de estado
            cambio_estado = estado_anterior != estado_nuevo
            resultado_api = None
            
            if cambio_estado:
                logger.info(f"Cambio de estado detectado: {estado_anterior} → {estado_nuevo}")
                
                # Caso 1: Criopreservado → Fresco (Descongelar)
                if estado_anterior == 'criopreservado' and estado_nuevo == 'fresco':
                    resultado_api = self._descongelar_ovocito(ovocito)
                    self._registrar_historial(ovocito, f"Descongelado (criopreservado → fresco)", request.user)
                
                # Caso 2: Fresco → Criopreservado (Congelar)
                elif estado_anterior == 'fresco' and estado_nuevo == 'criopreservado':
                    resultado_api = self._congelar_ovocito(ovocito)
                    self._registrar_historial(ovocito, f"Criopreservado (fresco → criopreservado)", request.user)
                
                # Caso 3: Criopreservado → Descartado
                elif estado_anterior == 'criopreservado' and estado_nuevo == 'descartado':
                    resultado_api = self._descongelar_ovocito(ovocito)
                    self._registrar_historial(ovocito, f"Descartado (previamente criopreservado)", request.user)
                
                # Caso 4: Fresco → Descartado
                elif estado_anterior == 'fresco' and estado_nuevo == 'descartado':
                    self._registrar_historial(ovocito, f"Descartado (previamente fresco)", request.user)
                
                # Otros cambios de estado
                else:
                    self._registrar_historial(ovocito, f"Cambio de estado: {estado_anterior} → {estado_nuevo}", request.user)

            logger.info(f"Ovocito actualizado: {ovocito.identificador}")
            
            response_data = {
                "success": True,
                "message": "Ovocito actualizado correctamente.",
                "data": serializer.data
            }
            
            if resultado_api:
                response_data["api_result"] = resultado_api
                
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error inesperado al actualizar ovocito: {str(e)}")
            return Response({
                "success": False,
                "message": f"Ocurrió un error al actualizar el ovocito: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def _congelar_ovocito(self, ovocito):
        """
        Llama a la API de Supabase para asignar tanque y rack al congelar.
        """
        try:
            res = requests.post(
                'https://ssewaxrnlmnyizqsbzxe.supabase.co/functions/v1/assign-ovocyte',
                json={
                    'nro_grupo': 1,
                    'ovocito_id': ovocito.identificador
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            logger.info(f"Respuesta API congelar: {res.status_code} - {res.text}")
            
            if res.ok:
                data = res.json()
                
                if isinstance(data, list) and len(data) > 0:
                    asignacion = data[0]
                    
                    # Guardar tanque y rack
                    ovocito.tanque_id = asignacion.get("tanque_id")
                    ovocito.rack_id = asignacion.get("rack_id")
                    ovocito.save()
                    
                    logger.info(f"Ovocito congelado y asignado: Tanque {ovocito.tanque_id}, Rack {ovocito.rack_id}")
                    return {
                        "action": "congelar",
                        "tanque_id": ovocito.tanque_id,
                        "rack_id": ovocito.rack_id
                    }
            else:
                logger.warning(f"API de congelación falló: {res.status_code} - {res.text}")
                return {"action": "congelar", "error": res.text}
                
        except requests.RequestException as e:
            logger.error(f"Error llamando API de congelación: {str(e)}")
            return {"action": "congelar", "error": str(e)}
        
        return None

    def _descongelar_ovocito(self, ovocito):
        """
        Llama a la API de Supabase para liberar el espacio al descongelar.
        Primero consulta la posición actual del ovocito.
        """
        try:
            # Paso 1: Consultar posición actual
            res_consulta = requests.post(
                'https://ssewaxrnlmnyizqsbzxe.supabase.co/functions/v1/get-ovocito-posicion',
                json={
                    'nro_grupo': '1',
                    'ovocito_id': ovocito.identificador
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            logger.info(f"Respuesta API consultar posición: {res_consulta.status_code} - {res_consulta.text}")
            
            if not res_consulta.ok:
                logger.warning(f"No se pudo consultar la posición del ovocito: {res_consulta.status_code}")
                return {"action": "descongelar", "error": "No se encontró la posición del ovocito"}
            
            posicion_data = res_consulta.json()
            
            # Validar que tengamos los datos necesarios
            if not posicion_data or len(posicion_data) == 0:
                logger.warning("No se encontró posición asignada para el ovocito")
                return {"action": "descongelar", "error": "Ovocito no tiene posición asignada"}
            
            posicion = posicion_data[0] if isinstance(posicion_data, list) else posicion_data
            tanque_id = posicion.get('tanque_id')
            rack_id = posicion.get('rack_id')
            
            if not tanque_id or not rack_id:
                logger.warning("Datos de posición incompletos")
                return {"action": "descongelar", "error": "Datos de posición incompletos"}
            
            # Paso 2: Liberar la posición usando deallocate-ovocyte
            res_liberar = requests.post(
                'https://ssewaxrnlmnyizqsbzxe.supabase.co/functions/v1/deallocate-ovocyte',
                json={
                    'ovocito_id': ovocito.identificador,
                    'nro_grupo': '1',
                    'id_tanque': tanque_id,
                    'id_rack': rack_id
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            logger.info(f"Respuesta API liberar posición: {res_liberar.status_code} - {res_liberar.text}")
            
            if res_liberar.ok:
                # Limpiar tanque y rack en la BD local
                ovocito.tanque_id = None
                ovocito.rack_id = None
                ovocito.save()
                
                logger.info(f"Ovocito descongelado y liberado del almacenamiento (Tanque {tanque_id}, Rack {rack_id})")
                return {
                    "action": "descongelar",
                    "message": "Espacio liberado correctamente",
                    "tanque_liberado": tanque_id,
                    "rack_liberado": rack_id
                }
            else:
                logger.warning(f"API de liberación falló: {res_liberar.status_code} - {res_liberar.text}")
                return {"action": "descongelar", "error": res_liberar.text}
                
        except requests.RequestException as e:
            logger.error(f"Error llamando API de descongelación: {str(e)}")
            return {"action": "descongelar", "error": str(e)}
        
        return None

    def _registrar_historial(self, ovocito, nota, usuario):
        """
        Registra un cambio en el historial del ovocito.
        """
        try:
            HistorialOvocito.objects.create(
                ovocito=ovocito,
                paciente=ovocito.paciente,
                usuario=usuario,
                estado=ovocito.tipo_estado,
                nota=nota
            )
            logger.info(f"Historial registrado: {nota}")
        except Exception as e:
            logger.error(f"Error al registrar historial: {str(e)}")
