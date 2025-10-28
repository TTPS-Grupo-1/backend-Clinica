from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'question', 'answer', 'user_name', 'user_age', 'user_gender', 'date_sent', 'timestamp']
        read_only_fields = ['id', 'timestamp']
        
class ChatMessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    user_name = serializers.CharField(max_length=100)
    user_age = serializers.IntegerField(min_value=1, max_value=120)
    user_gender = serializers.CharField(max_length=50, default='Femenino')
    date = serializers.DateField()