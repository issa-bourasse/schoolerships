"""
WebSocket URL routing for real-time communication
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/search/(?P<session_id>\w+)/$', consumers.SearchConsumer.as_asgi()),
    re_path(r'ws/ai-chat/$', consumers.AIChatConsumer.as_asgi()),
]
