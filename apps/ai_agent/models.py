"""
AI Agent Models

Track AI agent decisions, strategies, and performance
Real-time monitoring of autonomous scholarship hunting
"""

from django.db import models
from django.db.models import JSONField
import uuid


class AIAgent(models.Model):
    """
    AI Agent instance tracking
    Monitor autonomous decision-making and performance
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    agent_type = models.CharField(
        max_length=50,
        choices=[
            ('master', 'Master Coordinator'),
            ('searcher', 'Website Searcher'),
            ('analyzer', 'Content Analyzer'),
            ('validator', 'Data Validator'),
        ],
        db_index=True
    )
    
    # AI Model Configuration
    ai_model = models.CharField(max_length=100, default='deepseek-chat')
    model_provider = models.CharField(max_length=50, default='novita')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4000)
    
    # Status
    is_active = models.BooleanField(default=True)
    current_task = models.CharField(max_length=300, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Performance metrics
    tasks_completed = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    
    # Configuration
    system_prompt = models.TextField(blank=True)
    capabilities = JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_agents'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.name} ({self.agent_type})"


class AIDecision(models.Model):
    """
    Track AI agent decisions and reasoning
    Monitor autonomous decision-making process
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='decisions')
    
    # Decision context
    decision_type = models.CharField(
        max_length=50,
        choices=[
            ('website_discovery', 'Website Discovery'),
            ('content_analysis', 'Content Analysis'),
            ('eligibility_check', 'Eligibility Check'),
            ('relevance_scoring', 'Relevance Scoring'),
            ('strategy_adjustment', 'Strategy Adjustment'),
        ],
        db_index=True
    )
    
    # Input and output
    input_data = JSONField(default=dict)
    output_data = JSONField(default=dict)
    reasoning = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    # Execution details
    processing_time = models.FloatField(default=0.0)
    tokens_used = models.IntegerField(default=0)
    cost_estimate = models.FloatField(default=0.0)
    
    # Results
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_decisions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'decision_type']),
            models.Index(fields=['success', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent.name}: {self.decision_type} ({self.created_at})"


class SearchStrategy(models.Model):
    """
    AI-generated search strategies
    Dynamic strategy adaptation based on results
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Strategy configuration
    target_websites = JSONField(default=list)
    search_keywords = JSONField(default=list)
    priority_countries = JSONField(default=list)
    priority_fields = JSONField(default=list)
    
    # Execution parameters
    max_concurrent_requests = models.IntegerField(default=10)
    request_delay = models.FloatField(default=1.0)
    timeout_seconds = models.IntegerField(default=30)
    
    # Performance tracking
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    scholarships_found = models.IntegerField(default=0)
    
    # AI generation info
    generated_by_ai = models.BooleanField(default=True)
    ai_reasoning = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_strategies'
        ordering = ['-success_rate', '-scholarships_found']
    
    def __str__(self):
        return f"Strategy: {self.name}"


class AIThought(models.Model):
    """
    AI agent thinking process
    Real-time thoughts and reasoning for user visibility
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='thoughts')
    
    # Thought content
    thought_type = models.CharField(
        max_length=50,
        choices=[
            ('planning', 'Strategic Planning'),
            ('analysis', 'Content Analysis'),
            ('discovery', 'Website Discovery'),
            ('validation', 'Data Validation'),
            ('reflection', 'Self Reflection'),
            ('help_request', 'Help Request'),
        ],
        db_index=True
    )
    
    content = models.TextField()
    context = JSONField(default=dict, blank=True)
    
    # Metadata
    confidence = models.FloatField(default=0.0)
    importance = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    
    # User interaction
    requires_user_input = models.BooleanField(default=False)
    user_response = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_thoughts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'thought_type']),
            models.Index(fields=['requires_user_input', 'resolved']),
        ]
    
    def __str__(self):
        return f"{self.agent.name}: {self.thought_type} - {self.content[:50]}..."


class PerformanceMetric(models.Model):
    """
    AI agent performance tracking
    Real-time metrics and analytics
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='metrics')
    
    # Metric details
    metric_name = models.CharField(max_length=100, db_index=True)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50, blank=True)
    
    # Context
    context = JSONField(default=dict, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    
    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['agent', 'metric_name']),
            models.Index(fields=['recorded_at', 'metric_name']),
        ]
    
    def __str__(self):
        return f"{self.agent.name}: {self.metric_name} = {self.metric_value}"
