from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    question = models.TextField()
    answer = models.TextField()
    user_name = models.CharField(max_length=100)
    user_age = models.IntegerField()
    user_gender = models.CharField(max_length=50, default='Femenino')
    date_sent = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
