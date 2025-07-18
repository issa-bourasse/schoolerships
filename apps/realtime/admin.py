from django.contrib import admin
from .models import WebSocketConnection, RealtimeEvent


@admin.register(WebSocketConnection)
class WebSocketConnectionAdmin(admin.ModelAdmin):
    list_display = ['connection_id', 'connection_type', 'is_active', 'messages_sent', 'messages_received', 'connected_at']
    list_filter = ['connection_type', 'is_active']
    search_fields = ['connection_id', 'user_ip']
    readonly_fields = ['connected_at', 'last_activity', 'disconnected_at']


@admin.register(RealtimeEvent)
class RealtimeEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'priority', 'broadcast_to_all', 'delivery_count', 'sent_at']
    list_filter = ['event_type', 'priority', 'broadcast_to_all']
    search_fields = ['message']
    readonly_fields = ['sent_at']
