from django.contrib import admin
from .models import Scholarship, SearchSession, WebsiteTarget


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'country', 'tunisia_eligible', 'funding_type', 'overall_relevance_score', 'is_active']
    list_filter = ['tunisia_eligible', 'funding_type', 'academic_level', 'is_active', 'field_of_study']
    search_fields = ['name', 'provider', 'country', 'field_of_study']
    readonly_fields = ['id', 'scraped_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'provider', 'country', 'region')
        }),
        ('Eligibility', {
            'fields': ('tunisia_eligible', 'eligible_countries')
        }),
        ('Academic Details', {
            'fields': ('field_of_study', 'academic_level', 'duration')
        }),
        ('Relevance Scores', {
            'fields': ('ai_relevance_score', 'web_dev_relevance_score', 'it_relevance_score', 'overall_relevance_score')
        }),
        ('Funding', {
            'fields': ('funding_type', 'funding_amount', 'funding_coverage')
        }),
        ('Application', {
            'fields': ('application_deadline', 'application_url', 'application_process', 'required_documents')
        }),
        ('Requirements', {
            'fields': ('language_requirements', 'gpa_requirement', 'age_requirement', 'other_requirements')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone', 'contact_website')
        }),
        ('Metadata', {
            'fields': ('source_url', 'source_website', 'scraped_at', 'updated_at', 'verified_at')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'verification_notes', 'ai_processed', 'ai_processing_notes')
        }),
    )


@admin.register(SearchSession)
class SearchSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'status', 'scholarships_found', 'websites_searched', 'started_at']
    list_filter = ['status', 'ai_model_used']
    search_fields = ['session_name']
    readonly_fields = ['started_at', 'ended_at']


@admin.register(WebsiteTarget)
class WebsiteTargetAdmin(admin.ModelAdmin):
    list_display = ['domain', 'website_type', 'country', 'scholarships_found', 'success_rate', 'is_active']
    list_filter = ['website_type', 'country', 'is_active', 'is_blocked']
    search_fields = ['domain', 'url']
    readonly_fields = ['discovered_at', 'last_scraped']
