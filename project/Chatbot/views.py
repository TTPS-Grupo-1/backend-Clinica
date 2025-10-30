from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatMessageCreateSerializer
from .config import CHATBOT_API_URL, CHATBOT_API_KEY
import requests
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """Obtener el historial de mensajes del usuario autenticado"""
    try:
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        
        return JsonResponse({
            'success': True,
            'messages': serializer.data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Enviar mensaje al chatbot y guardar la conversación"""
    try:
        serializer = ChatMessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'success': False,
                'error': 'Datos inválidos',
                'details': serializer.errors
            }, status=400)
            
        validated_data = serializer.validated_data
        message = validated_data['message']
        user_name = validated_data['user_name']
        user_age = validated_data['user_age']
        user_gender = validated_data.get('user_gender', 'Femenino')
        date = validated_data['date']
        
        # Obtener ID del paciente
        patient_id = request.user.id if request.user.id else 1
        
        # Llamar a la API externa para obtener la respuesta
        api_response = call_external_api(message, user_name, user_age, date, user_gender, patient_id)
        
        # Guardar el mensaje en la base de datos
        chat_message = ChatMessage.objects.create(
            user=request.user,
            question=message,
            answer=api_response.get('response', 'Lo siento, no pude procesar tu mensaje.'),
            user_name=user_name,
            user_age=user_age,
            user_gender=user_gender,
            date_sent=date
        )
        
        serializer = ChatMessageSerializer(chat_message)
        
        return JsonResponse({
            'success': True,
            'message': serializer.data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def call_external_api(message, user_name, user_age, date, user_gender="Femenino", patient_id=1):
    """
    Función para llamar a la API externa del chatbot
    Envía el formato completo esperado por la API de Supabase
    """
    try:
        # Si no hay configuración de API, usar respuestas de ejemplo
        if not CHATBOT_API_URL or not CHATBOT_API_KEY:
            print("Warning: No chatbot API configured, using example responses")
            responses = [
                f"Hola {user_name}, entiendo tu consulta sobre '{message}'. Como tienes {user_age} años, te recomiendo que consultes con un especialista.",
                f"Gracias por tu pregunta, {user_name}. Basándome en tu edad ({user_age} años), puedo sugerirte algunas opciones.",
                f"Estimado/a {user_name}, tu consulta sobre '{message[:50]}...' es muy importante. A los {user_age} años, es recomendable considerar varios factores."
            ]
            
            import hashlib
            hash_obj = hashlib.md5(message.encode())
            response_index = int(hash_obj.hexdigest(), 16) % len(responses)
            return {"response": responses[response_index]}
        
        # Calcular fecha de nacimiento aproximada basándose en la edad
        from datetime import datetime, timedelta
        current_year = datetime.now().year
        birth_year = current_year - user_age
        birth_date = f"{birth_year}-01-01"  # Fecha aproximada
        
        # Llamar a la API externa configurada con el formato esperado
        payload = {
            "patientId": patient_id,
            "patientName": user_name,
            "birthDate": birth_date,
            "gender": user_gender,
            "messages": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": message
                        }
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CHATBOT_API_KEY}',
            'apikey': CHATBOT_API_KEY  # Para Supabase
        }
        
        response = requests.post(CHATBOT_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Extraer la respuesta del formato devuelto por tu API
            if "respuesta" in data:
                return {"response": data["respuesta"]}
            elif "response" in data:
                return {"response": data["response"]}
            elif "text" in data:
                return {"response": data["text"]}
            else:
                # Si no encontramos el campo esperado, devolver toda la respuesta como string
                return {"response": str(data)}
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return {"response": f"Error del servidor de chat: {response.status_code}"}
        
    except requests.exceptions.Timeout:
        return {"response": "La consulta tardó demasiado. Por favor intenta nuevamente."}
    except requests.exceptions.RequestException as e:
        print(f"Error calling external API: {e}")
        return {"response": "Lo siento, hubo un problema de conexión con el servicio de chat."}
