from django.contrib import admin
from .models import ScrapingSession, ProxyServer, ScrapingRule, RateLimitTracker, ContentCache


@admin.register(ScrapingSession)
class ScrapingSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'target_url', 'status', 'scholarships_found', 'duration_seconds', 'started_at']
    list_filter = ['status', 'scraper_type']
    search_fields = ['session_name', 'target_url']
    readonly_fields = ['started_at', 'ended_at']


@admin.register(ProxyServer)
class ProxyServerAdmin(admin.ModelAdmin):
    list_display = ['host', 'port', 'proxy_type', 'country', 'success_rate', 'is_active', 'is_blocked']
    list_filter = ['proxy_type', 'country', 'is_active', 'is_blocked']
    search_fields = ['host', 'provider']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ScrapingRule)
class ScrapingRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'success_rate', 'scholarships_extracted', 'is_active', 'generated_by_ai']
    list_filter = ['generated_by_ai', 'is_active']
    search_fields = ['name', 'domain']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(RateLimitTracker)
class RateLimitTrackerAdmin(admin.ModelAdmin):
    list_display = ['domain', 'requests_per_minute', 'current_minute_count', 'is_blocked', 'last_request']
    list_filter = ['is_blocked', 'detected_rate_limit']
    search_fields = ['domain']
    readonly_fields = ['updated_at']


@admin.register(ContentCache)
class ContentCacheAdmin(admin.ModelAdmin):
    list_display = ['url', 'status_code', 'content_length', 'hit_count', 'cached_at', 'expires_at']
    list_filter = ['status_code', 'is_valid']
    search_fields = ['url']
    readonly_fields = ['cached_at', 'url_hash']
