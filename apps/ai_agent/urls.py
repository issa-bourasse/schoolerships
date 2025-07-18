"""
AI Agent URL Configuration
"""

from django.urls import path
from . import views

app_name = 'ai_agent'

urlpatterns = [
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/<uuid:agent_id>/', views.agent_detail, name='agent_detail'),
    path('start-live-hunt/', views.start_live_hunt, name='start_live_hunt'),
    path('stop-live-hunt/', views.stop_live_hunt, name='stop_live_hunt'),
    path('hunt-status/', views.hunt_status, name='hunt_status'),
    path('statistics/', views.agent_statistics, name='agent_statistics'),
]
