from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.chat_history, name='chat_history'),
    path('message/', views.send_message, name='send_message'),
]