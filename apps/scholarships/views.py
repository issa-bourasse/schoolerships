"""
Scholarship API Views

REST API endpoints for scholarship data and search management
Real-time integration with AI agents and web scraping
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Scholarship, SearchSession, WebsiteTarget
from .serializers import ScholarshipSerializer, SearchSessionSerializer, WebsiteTargetSerializer
from .services import ScholarshipSearchOrchestrator
import asyncio
import logging

logger = logging.getLogger(__name__)


class ScholarshipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for scholarship data
    Supports filtering, searching, and real-time updates
    """
    
    queryset = Scholarship.objects.filter(is_active=True).order_by('-overall_relevance_score', '-scraped_at')
    serializer_class = ScholarshipSerializer
    permission_classes = [AllowAny]  # Open access for demo
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering options
    filterset_fields = {
        'tunisia_eligible': ['exact'],
        'funding_type': ['exact', 'in'],
        'academic_level': ['exact', 'in'],
        'field_of_study': ['icontains'],
        'country': ['exact', 'in'],
        'overall_relevance_score': ['gte', 'lte'],
        'ai_relevance_score': ['gte', 'lte'],
        'web_dev_relevance_score': ['gte', 'lte'],
        'it_relevance_score': ['gte', 'lte'],
    }
    
    # Search fields
    search_fields = ['name', 'provider', 'field_of_study', 'country', 'funding_coverage']
    
    # Ordering options
    ordering_fields = [
        'overall_relevance_score', 'ai_relevance_score', 'web_dev_relevance_score',
        'it_relevance_score', 'scraped_at', 'application_deadline'
    ]
    ordering = ['-overall_relevance_score', '-scraped_at']
    
    def get_queryset(self):
        """
        Customize queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by deadline status
        deadline_filter = self.request.query_params.get('deadline_status')
        if deadline_filter == 'active':
            queryset = queryset.filter(
                Q(application_deadline__isnull=True) | 
                Q(application_deadline__gt=timezone.now())
            )
        elif deadline_filter == 'expired':
            queryset = queryset.filter(
                application_deadline__isnull=False,
                application_deadline__lte=timezone.now()
            )
        
        # Filter by relevance category
        relevance_category = self.request.query_params.get('relevance_category')
        if relevance_category == 'ai':
            queryset = queryset.filter(ai_relevance_score__gte=0.3)
        elif relevance_category == 'web_dev':
            queryset = queryset.filter(web_dev_relevance_score__gte=0.3)
        elif relevance_category == 'it':
            queryset = queryset.filter(it_relevance_score__gte=0.3)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get scholarship statistics
        """
        try:
            queryset = self.get_queryset()
            
            stats = {
                'total_scholarships': queryset.count(),
                'tunisia_eligible': queryset.filter(tunisia_eligible=True).count(),
                'fully_funded': queryset.filter(funding_type='full').count(),
                'ai_relevant': queryset.filter(ai_relevance_score__gte=0.3).count(),
                'web_dev_relevant': queryset.filter(web_dev_relevance_score__gte=0.3).count(),
                'it_relevant': queryset.filter(it_relevance_score__gte=0.3).count(),
                'active_deadlines': queryset.filter(
                    Q(application_deadline__isnull=True) | 
                    Q(application_deadline__gt=timezone.now())
                ).count(),
                'by_country': list(
                    queryset.values('country')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'by_academic_level': list(
                    queryset.values('academic_level')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                ),
                'by_funding_type': list(
                    queryset.values('funding_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                )
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error getting scholarship statistics: {str(e)}")
            return Response(
                {'error': 'Failed to get statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def tunisia_scholarships(self, request):
        """
        Get scholarships specifically for Tunisia students
        """
        try:
            queryset = self.get_queryset().filter(tunisia_eligible=True)
            
            # Apply additional filters
            field_filter = request.query_params.get('field')
            if field_filter:
                if field_filter == 'ai':
                    queryset = queryset.filter(ai_relevance_score__gte=0.3)
                elif field_filter == 'web_dev':
                    queryset = queryset.filter(web_dev_relevance_score__gte=0.3)
                elif field_filter == 'it':
                    queryset = queryset.filter(it_relevance_score__gte=0.3)
            
            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting Tunisia scholarships: {str(e)}")
            return Response(
                {'error': 'Failed to get Tunisia scholarships'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for search session management
    Monitor AI agent search progress
    """
    
    queryset = SearchSession.objects.all().order_by('-started_at')
    serializer_class = SearchSessionSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def start_search(self, request):
        """
        Start a new AI-powered scholarship search
        """
        try:
            session_name = request.data.get('session_name', 'AI Scholarship Hunt')
            target_scholarships = request.data.get('target_scholarships', 10000)
            
            # Create orchestrator and start search
            orchestrator = ScholarshipSearchOrchestrator(session_name)
            
            # Start search asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_id = loop.run_until_complete(
                orchestrator.start_search(target_scholarships)
            )
            
            return Response({
                'success': True,
                'session_id': session_id,
                'message': 'Scholarship search started successfully'
            })
            
        except Exception as e:
            logger.error(f"Error starting search: {str(e)}")
            return Response(
                {'error': f'Failed to start search: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stop_search(self, request, pk=None):
        """
        Stop a running search session
        """
        try:
            session = self.get_object()
            
            if session.status != 'running':
                return Response(
                    {'error': 'Search session is not running'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # TODO: Implement search stopping mechanism
            session.status = 'paused'
            session.save()
            
            return Response({
                'success': True,
                'message': 'Search session stopped'
            })
            
        except Exception as e:
            logger.error(f"Error stopping search: {str(e)}")
            return Response(
                {'error': f'Failed to stop search: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Get real-time progress of a search session
        """
        try:
            session = self.get_object()
            
            progress_data = {
                'session_id': str(session.id),
                'session_name': session.session_name,
                'status': session.status,
                'scholarships_found': session.scholarships_found,
                'target_scholarships': session.target_scholarships,
                'websites_searched': session.websites_searched,
                'progress_percentage': min(
                    (session.scholarships_found / session.target_scholarships) * 100,
                    100
                ) if session.target_scholarships > 0 else 0,
                'started_at': session.started_at,
                'duration_seconds': (
                    (session.ended_at or timezone.now()) - session.started_at
                ).total_seconds(),
                'success_rate': session.success_rate,
                'ai_model_used': session.ai_model_used
            }
            
            return Response(progress_data)
            
        except Exception as e:
            logger.error(f"Error getting search progress: {str(e)}")
            return Response(
                {'error': 'Failed to get search progress'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WebsiteTargetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for website target management
    Monitor discovered websites and scraping performance
    """
    
    queryset = WebsiteTarget.objects.all().order_by('-scholarships_found', '-last_scraped')
    serializer_class = WebsiteTargetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    filterset_fields = ['website_type', 'country', 'is_active', 'is_blocked', 'discovered_by_ai']
    search_fields = ['domain', 'url']
    
    @action(detail=False, methods=['get'])
    def performance_stats(self, request):
        """
        Get website scraping performance statistics
        """
        try:
            queryset = self.get_queryset()
            
            stats = {
                'total_websites': queryset.count(),
                'active_websites': queryset.filter(is_active=True).count(),
                'blocked_websites': queryset.filter(is_blocked=True).count(),
                'ai_discovered': queryset.filter(discovered_by_ai=True).count(),
                'total_scholarships_found': sum(
                    website.scholarships_found for website in queryset
                ),
                'by_website_type': list(
                    queryset.values('website_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                ),
                'top_performers': list(
                    queryset.filter(scholarships_found__gt=0)
                    .order_by('-scholarships_found')[:10]
                    .values('domain', 'scholarships_found', 'success_rate')
                )
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error getting website performance stats: {str(e)}")
            return Response(
                {'error': 'Failed to get performance statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
