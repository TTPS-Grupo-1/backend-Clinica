# Configuración del Chatbot
# 
# Para conectar tu chatbot a una API externa, configura estas variables de entorno:

import os

CHATBOT_API_URL = os.getenv('CHATBOT_API_URL', 'https://tu-api-chatbot.com/chat')
CHATBOT_API_KEY = os.getenv('CHATBOT_API_KEY', '')

