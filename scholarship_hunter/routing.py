"""
WebSocket URL routing for real-time features
"""

from django.urls import re_path
from apps.ai_agent.consumers import AIHunterConsumer, DashboardConsumer

websocket_urlpatterns = [
    re_path(r'ws/ai-hunter/$', AIHunterConsumer.as_asgi()),
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
]
