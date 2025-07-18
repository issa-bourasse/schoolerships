"""
URL configuration for scholarship_hunter project.

AI-Powered Scholarship Hunter System
Main URL routing for all applications
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def api_health(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'AI Scholarship Hunter',
        'version': '1.0.0'
    })

@require_http_methods(["GET"])
def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'name': 'AI Scholarship Hunter API',
        'description': 'Autonomous AI-powered scholarship discovery system',
        'version': '1.0.0',
        'endpoints': {
            'scholarships': '/api/scholarships/',
            'search_sessions': '/api/search-sessions/',
            'website_targets': '/api/website-targets/',
            'websocket': '/ws/dashboard/',
            'admin': '/admin/',
            'health': '/health/'
        },
        'features': [
            'AI-powered scholarship discovery',
            'Real-time search progress',
            'Tunisia eligibility filtering',
            'Field-specific relevance scoring',
            'Autonomous web scraping',
            'Live dashboard updates'
        ]
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints
    path('', include('apps.scholarships.urls')),
    path('api/ai-agent/', include('apps.ai_agent.urls')),

    # Health and info endpoints
    path('health/', api_health, name='api_health'),
    path('api/info/', api_info, name='api_info'),

    # Django RQ (background tasks)
    path('django-rq/', include('django_rq.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
