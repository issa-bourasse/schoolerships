"""
WebSocket Consumers for Real-time AI Agent Communication
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .live_hunter import LiveScholarshipHunter


class AIHunterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for live AI scholarship hunting
    Provides real-time updates of AI agent activities
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunter = None
        self.hunting_task = None

    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()
        
        # Initialize live hunter
        self.hunter = LiveScholarshipHunter(self.channel_name)
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to AI Hunter'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.hunter:
            self.hunter.stop_hunting()
        
        if self.hunting_task and not self.hunting_task.done():
            self.hunting_task.cancel()

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'start_hunt':
                await self.start_hunt(data.get('config', {}))
            elif message_type == 'stop_hunt':
                await self.stop_hunt()
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection alive'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON received'
            }))

    async def start_hunt(self, config):
        """Start the AI hunting process"""
        if self.hunting_task and not self.hunting_task.done():
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Hunt already in progress'
            }))
            return
        
        # Start hunting in background task
        self.hunting_task = asyncio.create_task(
            self.hunter.start_hunting(config)
        )
        
        await self.send(text_data=json.dumps({
            'type': 'hunt_started',
            'message': 'AI hunt started successfully'
        }))

    async def stop_hunt(self):
        """Stop the AI hunting process"""
        if self.hunter:
            self.hunter.stop_hunting()
        
        if self.hunting_task and not self.hunting_task.done():
            self.hunting_task.cancel()
        
        await self.send(text_data=json.dumps({
            'type': 'hunt_stopped',
            'message': 'AI hunt stopped'
        }))

    async def hunter_message(self, event):
        """Handle messages from the hunter"""
        await self.send(text_data=json.dumps(event['message']))


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for dashboard real-time updates
    """
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.room_group_name = 'dashboard'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        """Leave room group"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            pass

    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))
