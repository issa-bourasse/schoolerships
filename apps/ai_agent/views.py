"""
AI Agent Views
API endpoints for AI agent management and live hunting
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
from .models import AIAgent
from apps.scholarships.models import SearchSession
from .services import ScholarshipHunterAI


@api_view(['GET'])
def agent_list(request):
    """Get list of AI agents"""
    agents = AIAgent.objects.all().order_by('-created_at')
    
    agent_data = []
    for agent in agents:
        agent_data.append({
            'id': str(agent.id),
            'name': agent.name,
            'agent_type': agent.agent_type,
            'ai_model': agent.ai_model,
            'model_provider': agent.model_provider,
            'status': agent.status,
            'success_rate': agent.success_rate,
            'total_decisions': agent.total_decisions,
            'created_at': agent.created_at.isoformat(),
            'last_active': agent.last_active.isoformat() if agent.last_active else None
        })
    
    return Response({
        'agents': agent_data,
        'total_count': len(agent_data)
    })


@api_view(['GET'])
def agent_detail(request, agent_id):
    """Get detailed information about a specific agent"""
    try:
        agent = AIAgent.objects.get(id=agent_id)
        
        # Get recent decisions
        recent_decisions = agent.decisions.order_by('-created_at')[:10]
        decisions_data = []
        
        for decision in recent_decisions:
            decisions_data.append({
                'id': str(decision.id),
                'decision_type': decision.decision_type,
                'reasoning': decision.reasoning,
                'confidence_score': decision.confidence_score,
                'success': decision.success,
                'created_at': decision.created_at.isoformat()
            })
        
        return Response({
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
                'agent_type': agent.agent_type,
                'ai_model': agent.ai_model,
                'model_provider': agent.model_provider,
                'status': agent.status,
                'success_rate': agent.success_rate,
                'total_decisions': agent.total_decisions,
                'created_at': agent.created_at.isoformat(),
                'last_active': agent.last_active.isoformat() if agent.last_active else None
            },
            'recent_decisions': decisions_data
        })
        
    except AIAgent.DoesNotExist:
        return Response(
            {'error': 'Agent not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def start_live_hunt(request):
    """Start a live AI hunting session"""
    try:
        config = request.data
        
        # Create a search session
        session = SearchSession.objects.create(
            session_name=f"Live Hunt {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            target_scholarships=config.get('max_scholarships', 50),
            status='running',
            ai_model_used='deepseek/deepseek-v3-0324',
            search_strategy=f"Live hunting for {', '.join(config.get('target_countries', ['Tunisia']))} students in {', '.join(config.get('fields', ['Computer Science', 'AI']))}"
        )
        
        return Response({
            'success': True,
            'message': 'Live hunt started successfully',
            'session_id': str(session.id),
            'config': config
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start hunt: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def stop_live_hunt(request):
    """Stop the current live hunting session"""
    try:
        # Find active sessions and mark as completed
        active_sessions = SearchSession.objects.filter(status='running')
        for session in active_sessions:
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
        
        return Response({
            'success': True,
            'message': 'Live hunt stopped successfully',
            'stopped_sessions': len(active_sessions)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to stop hunt: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def hunt_status(request):
    """Get current hunting status"""
    try:
        active_sessions = SearchSession.objects.filter(status='running')

        if active_sessions.exists():
            session = active_sessions.first()
            return Response({
                'hunting': True,
                'session': {
                    'id': str(session.id),
                    'name': session.session_name,
                    'start_time': session.started_at.isoformat(),
                    'scholarships_found': session.scholarships_found,
                    'websites_visited': session.websites_searched,
                    'target_scholarships': session.target_scholarships,
                    'search_strategy': session.search_strategy
                }
            })
        else:
            return Response({
                'hunting': False,
                'message': 'No active hunting sessions'
            })
            
    except Exception as e:
        return Response(
            {'error': f'Failed to get status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def agent_statistics(request):
    """Get AI agent statistics"""
    try:
        total_agents = AIAgent.objects.count()
        active_agents = AIAgent.objects.filter(status='active').count()
        total_decisions = sum(agent.total_decisions for agent in AIAgent.objects.all())
        
        # Average success rate
        agents_with_decisions = AIAgent.objects.filter(total_decisions__gt=0)
        avg_success_rate = 0
        if agents_with_decisions.exists():
            avg_success_rate = sum(agent.success_rate for agent in agents_with_decisions) / agents_with_decisions.count()
        
        return Response({
            'total_agents': total_agents,
            'active_agents': active_agents,
            'total_decisions': total_decisions,
            'average_success_rate': round(avg_success_rate, 2),
            'agent_types': {
                'master': AIAgent.objects.filter(agent_type='master').count(),
                'content_analyzer': AIAgent.objects.filter(agent_type='content_analyzer').count(),
                'validator': AIAgent.objects.filter(agent_type='validator').count(),
                'coordinator': AIAgent.objects.filter(agent_type='coordinator').count()
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get statistics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
