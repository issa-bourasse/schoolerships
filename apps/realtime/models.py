"""
Real-time Communication Models

Track WebSocket connections and real-time events
Monitor user interactions and system notifications
"""

from django.db import models
from django.db.models import JSONField
import uuid


class WebSocketConnection(models.Model):
    """
    Track active WebSocket connections
    Monitor real-time communication
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Connection details
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Session info
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    connection_type = models.CharField(
        max_length=50,
        choices=[
            ('dashboard', 'Dashboard Monitor'),
            ('search', 'Search Session'),
            ('admin', 'Admin Panel'),
        ],
        default='dashboard'
    )
    
    # Metrics
    messages_sent = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'websocket_connections'
        ordering = ['-connected_at']
    
    def __str__(self):
        return f"WebSocket: {self.connection_id} ({self.connection_type})"


class RealtimeEvent(models.Model):
    """
    Track real-time events sent to clients
    Monitor system notifications and updates
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event details
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('scholarship_found', 'Scholarship Found'),
            ('website_discovered', 'Website Discovered'),
            ('ai_thinking', 'AI Thinking'),
            ('search_progress', 'Search Progress'),
            ('error_occurred', 'Error Occurred'),
            ('session_update', 'Session Update'),
        ],
        db_index=True
    )
    
    event_data = JSONField(default=dict)
    message = models.TextField(blank=True)
    
    # Targeting
    broadcast_to_all = models.BooleanField(default=True)
    target_connections = models.ManyToManyField(
        WebSocketConnection,
        blank=True,
        related_name='targeted_events'
    )
    
    # Metadata
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )
    
    # Delivery tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'realtime_events'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['event_type', 'sent_at']),
        ]
    
    def __str__(self):
        return f"Event: {self.event_type} - {self.message[:50]}..."
