"""
Scholarship App URLs

API routing for scholarship endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'scholarships', views.ScholarshipViewSet)
router.register(r'search-sessions', views.SearchSessionViewSet)
router.register(r'website-targets', views.WebsiteTargetViewSet)

app_name = 'scholarships'

urlpatterns = [
    path('api/', include(router.urls)),
]
