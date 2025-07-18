"""
Scholarship Serializers

DRF serializers for API data formatting
Optimized for frontend consumption
"""

from rest_framework import serializers
from .models import Scholarship, SearchSession, WebsiteTarget


class ScholarshipSerializer(serializers.ModelSerializer):
    """
    Serializer for scholarship data
    Includes computed fields and formatted data
    """
    
    relevance_category = serializers.ReadOnlyField()
    is_deadline_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'name', 'provider', 'country', 'region',
            'tunisia_eligible', 'eligible_countries',
            'field_of_study', 'academic_level',
            'ai_relevance_score', 'web_dev_relevance_score', 
            'it_relevance_score', 'overall_relevance_score',
            'relevance_category',
            'funding_type', 'funding_amount', 'funding_coverage',
            'application_deadline', 'is_deadline_active',
            'application_url', 'application_process', 'required_documents',
            'language_requirements', 'gpa_requirement', 'age_requirement',
            'other_requirements', 'duration', 'start_date', 'number_of_awards',
            'contact_email', 'contact_phone', 'contact_website',
            'source_url', 'source_website', 'scraped_at', 'updated_at',
            'is_active', 'is_verified'
        ]
        read_only_fields = ['id', 'scraped_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Customize serialized representation
        """
        data = super().to_representation(instance)
        
        # Format dates
        if data['application_deadline']:
            data['application_deadline'] = instance.application_deadline.isoformat()
        if data['start_date']:
            data['start_date'] = instance.start_date.isoformat()
        
        # Add computed fields
        data['days_until_deadline'] = None
        if instance.application_deadline:
            from django.utils import timezone
            delta = instance.application_deadline - timezone.now()
            if delta.days >= 0:
                data['days_until_deadline'] = delta.days
        
        # Format relevance scores as percentages
        data['ai_relevance_percentage'] = round(instance.ai_relevance_score * 100, 1)
        data['web_dev_relevance_percentage'] = round(instance.web_dev_relevance_score * 100, 1)
        data['it_relevance_percentage'] = round(instance.it_relevance_score * 100, 1)
        data['overall_relevance_percentage'] = round(instance.overall_relevance_score * 100, 1)
        
        return data


class ScholarshipSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for scholarship summaries
    Used in lists and search results
    """
    
    relevance_category = serializers.ReadOnlyField()
    is_deadline_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'name', 'provider', 'country',
            'tunisia_eligible', 'field_of_study', 'academic_level',
            'overall_relevance_score', 'relevance_category',
            'funding_type', 'application_deadline', 'is_deadline_active',
            'application_url', 'source_website', 'scraped_at'
        ]


class SearchSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for search session data
    Includes progress tracking and performance metrics
    """
    
    duration_seconds = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    scholarships_per_hour = serializers.SerializerMethodField()
    
    class Meta:
        model = SearchSession
        fields = [
            'id', 'session_name', 'started_at', 'ended_at',
            'duration_seconds', 'target_scholarships', 'scholarships_found',
            'progress_percentage', 'websites_searched', 'status',
            'ai_model_used', 'search_strategy', 'success_rate',
            'scholarships_per_hour', 'notes', 'error_log'
        ]
        read_only_fields = ['id', 'started_at', 'ended_at']
    
    def get_duration_seconds(self, obj):
        """Calculate session duration in seconds"""
        from django.utils import timezone
        end_time = obj.ended_at or timezone.now()
        return (end_time - obj.started_at).total_seconds()
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        if obj.target_scholarships == 0:
            return 0
        return min((obj.scholarships_found / obj.target_scholarships) * 100, 100)
    
    def get_scholarships_per_hour(self, obj):
        """Calculate scholarships found per hour"""
        duration_hours = self.get_duration_seconds(obj) / 3600
        if duration_hours == 0:
            return 0
        return round(obj.scholarships_found / duration_hours, 2)


class WebsiteTargetSerializer(serializers.ModelSerializer):
    """
    Serializer for website target data
    Includes performance metrics and discovery information
    """
    
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = WebsiteTarget
        fields = [
            'id', 'url', 'domain', 'website_type', 'country', 'language',
            'discovered_by_ai', 'discovery_method', 'discovered_at',
            'last_scraped', 'scrape_count', 'success_count', 'success_rate',
            'scholarships_found', 'is_active', 'is_blocked', 'block_reason'
        ]
        read_only_fields = ['id', 'discovered_at', 'last_scraped']
    
    def to_representation(self, instance):
        """
        Customize serialized representation
        """
        data = super().to_representation(instance)
        
        # Format dates
        if data['discovered_at']:
            data['discovered_at'] = instance.discovered_at.isoformat()
        if data['last_scraped']:
            data['last_scraped'] = instance.last_scraped.isoformat()
        
        # Add performance indicators
        data['performance_rating'] = 'excellent' if instance.success_rate > 80 else \
                                   'good' if instance.success_rate > 60 else \
                                   'fair' if instance.success_rate > 40 else 'poor'
        
        return data


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics
    Real-time system overview data
    """
    
    total_scholarships = serializers.IntegerField()
    tunisia_scholarships = serializers.IntegerField()
    fully_funded_scholarships = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    websites_discovered = serializers.IntegerField()
    ai_agents_active = serializers.IntegerField()
    
    # Recent activity
    scholarships_today = serializers.IntegerField()
    scholarships_this_week = serializers.IntegerField()
    websites_scraped_today = serializers.IntegerField()
    
    # Performance metrics
    average_relevance_score = serializers.FloatField()
    success_rate = serializers.FloatField()
    
    # Top categories
    top_countries = serializers.ListField(child=serializers.DictField())
    top_fields = serializers.ListField(child=serializers.DictField())
    top_providers = serializers.ListField(child=serializers.DictField())


class AIAgentStatusSerializer(serializers.Serializer):
    """
    Serializer for AI agent status information
    Real-time agent monitoring
    """
    
    agent_id = serializers.UUIDField()
    agent_name = serializers.CharField()
    agent_type = serializers.CharField()
    is_active = serializers.BooleanField()
    current_task = serializers.CharField()
    last_activity = serializers.DateTimeField()
    
    # Performance
    tasks_completed = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField()
    
    # Current thinking
    latest_thought = serializers.CharField(allow_blank=True)
    thought_type = serializers.CharField(allow_blank=True)
    confidence = serializers.FloatField()


class SearchProgressSerializer(serializers.Serializer):
    """
    Serializer for real-time search progress
    WebSocket and API progress updates
    """
    
    session_id = serializers.UUIDField()
    session_name = serializers.CharField()
    status = serializers.CharField()
    
    # Progress metrics
    scholarships_found = serializers.IntegerField()
    target_scholarships = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    websites_searched = serializers.IntegerField()
    
    # Timing
    started_at = serializers.DateTimeField()
    duration_seconds = serializers.FloatField()
    estimated_completion = serializers.DateTimeField(allow_null=True)
    
    # Current activity
    current_website = serializers.CharField(allow_blank=True)
    current_action = serializers.CharField(allow_blank=True)
    
    # Recent discoveries
    recent_scholarships = serializers.ListField(
        child=ScholarshipSummarySerializer(),
        max_length=5
    )
    
    # AI insights
    ai_thoughts = serializers.ListField(
        child=serializers.CharField(),
        max_length=3
    )
