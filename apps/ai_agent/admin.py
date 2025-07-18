from django.contrib import admin
from .models import AIAgent, AIDecision, SearchStrategy, AIThought, PerformanceMetric


@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent_type', 'ai_model', 'is_active', 'tasks_completed', 'success_rate', 'last_activity']
    list_filter = ['agent_type', 'ai_model', 'model_provider', 'is_active']
    search_fields = ['name', 'current_task']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']


@admin.register(AIDecision)
class AIDecisionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'decision_type', 'confidence_score', 'success', 'processing_time', 'created_at']
    list_filter = ['decision_type', 'success', 'agent']
    search_fields = ['reasoning']
    readonly_fields = ['created_at']


@admin.register(SearchStrategy)
class SearchStrategyAdmin(admin.ModelAdmin):
    list_display = ['name', 'success_rate', 'scholarships_found', 'times_used', 'is_active']
    list_filter = ['generated_by_ai', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIThought)
class AIThoughtAdmin(admin.ModelAdmin):
    list_display = ['agent', 'thought_type', 'importance', 'requires_user_input', 'resolved', 'created_at']
    list_filter = ['thought_type', 'importance', 'requires_user_input', 'resolved']
    search_fields = ['content']
    readonly_fields = ['created_at']


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['agent', 'metric_name', 'metric_value', 'metric_unit', 'recorded_at']
    list_filter = ['metric_name', 'agent']
    readonly_fields = ['recorded_at']
