"""
WebSocket Consumers for Real-time Communication

Handle real-time updates for dashboard, search progress, and AI chat
"""

import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for dashboard real-time updates
    Shows live search progress, AI thinking, and scholarship discoveries
    """
    
    async def connect(self):
        self.room_group_name = 'dashboard'
        self.connection_id = str(uuid.uuid4())
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Track connection
        await self.track_connection()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'connection_id': self.connection_id,
            'message': 'Connected to AI Scholarship Hunter Dashboard'
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update connection status
        await self.update_connection_status(False)
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            
            elif message_type == 'request_status':
                await self.send_status_update()
            
            # Update last activity
            await self.update_last_activity()
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    # Receive message from room group
    async def dashboard_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps(event))
    
    async def scholarship_found(self, event):
        """Handle scholarship found event"""
        await self.send(text_data=json.dumps({
            'type': 'scholarship_found',
            'data': event['data'],
            'timestamp': timezone.now().isoformat()
        }))
    
    async def ai_thinking(self, event):
        """Handle AI thinking event"""
        await self.send(text_data=json.dumps({
            'type': 'ai_thinking',
            'agent': event['agent'],
            'thought': event['thought'],
            'timestamp': timezone.now().isoformat()
        }))
    
    async def search_progress(self, event):
        """Handle search progress event"""
        await self.send(text_data=json.dumps({
            'type': 'search_progress',
            'progress': event['progress'],
            'timestamp': timezone.now().isoformat()
        }))
    
    @database_sync_to_async
    def track_connection(self):
        """Track WebSocket connection in database"""
        from .models import WebSocketConnection
        
        WebSocketConnection.objects.create(
            connection_id=self.connection_id,
            user_ip=self.scope.get('client', ['', ''])[0],
            user_agent=dict(self.scope.get('headers', {})).get(b'user-agent', b'').decode(),
            connection_type='dashboard'
        )
    
    @database_sync_to_async
    def update_connection_status(self, is_active):
        """Update connection status"""
        from .models import WebSocketConnection
        
        try:
            connection = WebSocketConnection.objects.get(connection_id=self.connection_id)
            connection.is_active = is_active
            if not is_active:
                connection.disconnected_at = timezone.now()
            connection.save()
        except WebSocketConnection.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_last_activity(self):
        """Update last activity timestamp"""
        from .models import WebSocketConnection
        
        try:
            connection = WebSocketConnection.objects.get(connection_id=self.connection_id)
            connection.last_activity = timezone.now()
            connection.messages_received += 1
            connection.save()
        except WebSocketConnection.DoesNotExist:
            pass
    
    async def send_status_update(self):
        """Send current system status"""
        status = await self.get_system_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status,
            'timestamp': timezone.now().isoformat()
        }))
    
    @database_sync_to_async
    def get_system_status(self):
        """Get current system status"""
        from apps.scholarships.models import Scholarship, SearchSession
        from apps.ai_agent.models import AIAgent
        
        try:
            total_scholarships = Scholarship.objects.filter(is_active=True).count()
            tunisia_scholarships = Scholarship.objects.filter(
                tunisia_eligible=True, 
                is_active=True
            ).count()
            active_sessions = SearchSession.objects.filter(status='running').count()
            active_agents = AIAgent.objects.filter(is_active=True).count()
            
            return {
                'total_scholarships': total_scholarships,
                'tunisia_scholarships': tunisia_scholarships,
                'active_sessions': active_sessions,
                'active_agents': active_agents
            }
        except Exception as e:
            return {'error': str(e)}


class SearchConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for specific search session updates
    """
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'search_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'get_session_status':
            await self.send_session_status()
    
    async def search_update(self, event):
        """Send search update to WebSocket"""
        await self.send(text_data=json.dumps(event))
    
    async def send_session_status(self):
        """Send current session status"""
        status = await self.get_session_status()
        await self.send(text_data=json.dumps({
            'type': 'session_status',
            'status': status,
            'timestamp': timezone.now().isoformat()
        }))
    
    @database_sync_to_async
    def get_session_status(self):
        """Get session status from database"""
        from apps.scholarships.models import SearchSession
        
        try:
            session = SearchSession.objects.get(id=self.session_id)
            return {
                'session_name': session.session_name,
                'status': session.status,
                'scholarships_found': session.scholarships_found,
                'websites_searched': session.websites_searched,
                'target_scholarships': session.target_scholarships,
                'started_at': session.started_at.isoformat(),
            }
        except SearchSession.DoesNotExist:
            return {'error': 'Session not found'}


class AIChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for AI chat interface
    Allow users to interact with AI agents
    """
    
    async def connect(self):
        self.room_group_name = 'ai_chat'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle chat messages from user"""
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        message_type = text_data_json.get('type', 'user_message')
        
        if message_type == 'user_message':
            # Process user message and get AI response
            await self.process_user_message(message)
    
    async def ai_response(self, event):
        """Send AI response to WebSocket"""
        await self.send(text_data=json.dumps(event))
    
    async def process_user_message(self, message):
        """Process user message and generate AI response"""
        # This would integrate with the AI agent system
        # For now, send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'message': f'AI received your message: {message}',
            'timestamp': timezone.now().isoformat()
        }))
        
        # TODO: Integrate with AI agent system to process the message
        # and generate appropriate responses
