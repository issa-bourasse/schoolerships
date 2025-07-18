"""
Scholarship Models

Core data models for storing scholarship information
Designed for 10,000+ scholarships with comprehensive data
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import URLValidator
import uuid


class Scholarship(models.Model):
    """
    Main scholarship model with comprehensive information
    Optimized for Tunisia eligibility and AI/IT fields
    """
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, db_index=True)
    provider = models.CharField(max_length=300, db_index=True)
    
    # Location and eligibility
    country = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=100, blank=True)
    tunisia_eligible = models.BooleanField(default=False, db_index=True)
    eligible_countries = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="List of eligible countries"
    )
    
    # Academic information
    field_of_study = models.CharField(max_length=200, db_index=True)
    academic_level = models.CharField(
        max_length=50,
        choices=[
            ('bachelor', 'Bachelor\'s Degree'),
            ('master', 'Master\'s Degree'),
            ('phd', 'PhD/Doctorate'),
            ('professional', 'Professional Development'),
            ('bootcamp', 'Bootcamp/Certificate'),
            ('any', 'Any Level'),
        ],
        db_index=True
    )
    
    # Field relevance scoring
    ai_relevance_score = models.FloatField(default=0.0, db_index=True)
    web_dev_relevance_score = models.FloatField(default=0.0, db_index=True)
    it_relevance_score = models.FloatField(default=0.0, db_index=True)
    overall_relevance_score = models.FloatField(default=0.0, db_index=True)
    
    # Funding information
    funding_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Fully Funded'),
            ('partial', 'Partially Funded'),
            ('tuition', 'Tuition Only'),
            ('living', 'Living Expenses Only'),
        ],
        default='full',
        db_index=True
    )
    funding_amount = models.CharField(max_length=200, blank=True)
    funding_coverage = models.TextField(blank=True)
    
    # Application details
    application_deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    application_url = models.URLField(max_length=1000, validators=[URLValidator()])
    application_process = models.TextField(blank=True)
    required_documents = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list
    )
    
    # Requirements
    language_requirements = models.CharField(max_length=200, blank=True)
    gpa_requirement = models.CharField(max_length=100, blank=True)
    age_requirement = models.CharField(max_length=100, blank=True)
    other_requirements = models.TextField(blank=True)
    
    # Program details
    duration = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    number_of_awards = models.CharField(max_length=100, blank=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_website = models.URLField(max_length=1000, blank=True)
    
    # Metadata
    source_url = models.URLField(max_length=1000, db_index=True)
    source_website = models.CharField(max_length=200, db_index=True)
    scraped_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    verification_notes = models.TextField(blank=True)
    
    # AI processing
    ai_processed = models.BooleanField(default=False, db_index=True)
    ai_processing_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'scholarships'
        ordering = ['-overall_relevance_score', '-scraped_at']
        indexes = [
            models.Index(fields=['tunisia_eligible', 'is_active']),
            models.Index(fields=['field_of_study', 'academic_level']),
            models.Index(fields=['funding_type', 'application_deadline']),
            models.Index(fields=['overall_relevance_score', 'tunisia_eligible']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.provider} ({self.country})"
    
    @property
    def is_deadline_active(self):
        """Check if application deadline is still active"""
        if not self.application_deadline:
            return True  # Assume active if no deadline specified
        from django.utils import timezone
        return self.application_deadline > timezone.now()
    
    @property
    def relevance_category(self):
        """Determine primary relevance category"""
        scores = {
            'AI': self.ai_relevance_score,
            'Web Development': self.web_dev_relevance_score,
            'IT': self.it_relevance_score,
        }
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'General'


class SearchSession(models.Model):
    """
    Track AI agent search sessions
    Monitor progress and performance
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=200)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    target_scholarships = models.IntegerField(default=10000)
    scholarships_found = models.IntegerField(default=0)
    websites_searched = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='running'
    )
    
    # AI agent information
    ai_model_used = models.CharField(max_length=100, blank=True)
    search_strategy = models.TextField(blank=True)
    
    # Performance metrics
    success_rate = models.FloatField(default=0.0)
    average_processing_time = models.FloatField(default=0.0)
    
    # Notes and logs
    notes = models.TextField(blank=True)
    error_log = models.TextField(blank=True)
    
    class Meta:
        db_table = 'search_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Search Session: {self.session_name} ({self.status})"


class WebsiteTarget(models.Model):
    """
    Track websites being scraped by AI agents
    Monitor success rates and performance
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=1000, unique=True)
    domain = models.CharField(max_length=200, db_index=True)
    website_type = models.CharField(
        max_length=50,
        choices=[
            ('university', 'University'),
            ('government', 'Government Portal'),
            ('foundation', 'Foundation/NGO'),
            ('company', 'Company'),
            ('database', 'Scholarship Database'),
            ('other', 'Other'),
        ],
        db_index=True
    )
    
    # Discovery information
    discovered_by_ai = models.BooleanField(default=True)
    discovery_method = models.CharField(max_length=100, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    # Performance tracking
    last_scraped = models.DateTimeField(null=True, blank=True)
    scrape_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    scholarships_found = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    
    # Metadata
    country = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'website_targets'
        ordering = ['-scholarships_found', '-last_scraped']
        indexes = [
            models.Index(fields=['domain', 'is_active']),
            models.Index(fields=['website_type', 'country']),
        ]
    
    def __str__(self):
        return f"{self.domain} ({self.website_type})"
    
    @property
    def success_rate(self):
        """Calculate scraping success rate"""
        if self.scrape_count == 0:
            return 0.0
        return (self.success_count / self.scrape_count) * 100
