from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_name', 'user_gender', 'user_age', 'timestamp', 'question_preview']
    list_filter = ['timestamp', 'user_age', 'user_gender']
    search_fields = ['user__username', 'user_name', 'question', 'answer']
    readonly_fields = ['timestamp']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Pregunta"
