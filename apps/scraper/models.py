"""
Web Scraper Models

Track scraping sessions, performance, and data extraction
Real-time monitoring of web scraping operations
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
import uuid


class ScrapingSession(models.Model):
    """
    Track individual scraping sessions
    Monitor performance and results
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=200)
    target_url = models.URLField(max_length=1000)
    
    # Session details
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Configuration
    scraper_type = models.CharField(
        max_length=50,
        choices=[
            ('requests', 'Requests + BeautifulSoup'),
            ('selenium', 'Selenium WebDriver'),
            ('aiohttp', 'Async HTTP'),
            ('playwright', 'Playwright'),
        ],
        default='aiohttp'
    )
    
    user_agent = models.CharField(max_length=500, blank=True)
    proxy_used = models.CharField(max_length=200, blank=True)
    
    # Results
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('timeout', 'Timeout'),
            ('blocked', 'Blocked'),
        ],
        default='running',
        db_index=True
    )
    
    scholarships_found = models.IntegerField(default=0)
    pages_scraped = models.IntegerField(default=0)
    errors_encountered = models.IntegerField(default=0)
    
    # Response details
    response_code = models.IntegerField(null=True, blank=True)
    response_size = models.IntegerField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # Metadata
    raw_data = JSONField(default=dict, blank=True)
    extracted_data = JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'scraping_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['target_url', 'status']),
        ]
    
    def __str__(self):
        return f"Scraping: {self.target_url} ({self.status})"


class ProxyServer(models.Model):
    """
    Manage proxy servers for scraping
    Rotate proxies to avoid detection
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.CharField(max_length=200)
    port = models.IntegerField()
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    
    # Proxy details
    proxy_type = models.CharField(
        max_length=20,
        choices=[
            ('http', 'HTTP'),
            ('https', 'HTTPS'),
            ('socks4', 'SOCKS4'),
            ('socks5', 'SOCKS5'),
        ],
        default='http'
    )
    
    country = models.CharField(max_length=100, blank=True)
    provider = models.CharField(max_length=100, blank=True)
    
    # Performance tracking
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    # Status
    is_blocked = models.BooleanField(default=False)
    blocked_websites = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proxy_servers'
        ordering = ['-success_count', 'average_response_time']
        unique_together = ['host', 'port']
    
    def __str__(self):
        return f"{self.host}:{self.port} ({self.proxy_type})"
    
    @property
    def success_rate(self):
        """Calculate proxy success rate"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100


class ScrapingRule(models.Model):
    """
    Define scraping rules for different websites
    AI-generated and human-defined extraction rules
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, db_index=True)
    
    # Rule configuration
    selectors = JSONField(default=dict, help_text="CSS/XPath selectors for data extraction")
    extraction_rules = JSONField(default=dict, help_text="Data extraction and transformation rules")
    
    # Behavior settings
    wait_time = models.FloatField(default=1.0)
    max_pages = models.IntegerField(default=10)
    follow_links = models.BooleanField(default=True)
    
    # AI generation
    generated_by_ai = models.BooleanField(default=False)
    ai_confidence = models.FloatField(default=0.0)
    ai_reasoning = models.TextField(blank=True)
    
    # Performance
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    scholarships_extracted = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scraping_rules'
        ordering = ['-success_rate', '-scholarships_extracted']
        indexes = [
            models.Index(fields=['domain', 'is_active']),
        ]
    
    def __str__(self):
        return f"Rule: {self.name} ({self.domain})"


class RateLimitTracker(models.Model):
    """
    Track rate limiting for different domains
    Prevent being blocked by respecting limits
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=200, unique=True, db_index=True)
    
    # Rate limiting
    requests_per_minute = models.IntegerField(default=10)
    requests_per_hour = models.IntegerField(default=100)
    current_minute_count = models.IntegerField(default=0)
    current_hour_count = models.IntegerField(default=0)
    
    # Timing
    last_request = models.DateTimeField(null=True, blank=True)
    minute_reset = models.DateTimeField(null=True, blank=True)
    hour_reset = models.DateTimeField(null=True, blank=True)
    
    # Blocking status
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    block_reason = models.CharField(max_length=200, blank=True)
    
    # Detection
    detected_rate_limit = models.BooleanField(default=False)
    rate_limit_response = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rate_limit_trackers'
        ordering = ['domain']
    
    def __str__(self):
        return f"Rate Limit: {self.domain}"
    
    def can_make_request(self):
        """Check if we can make a request to this domain"""
        from django.utils import timezone
        now = timezone.now()
        
        if self.is_blocked and self.blocked_until and now < self.blocked_until:
            return False
        
        # Reset counters if needed
        if self.minute_reset and now > self.minute_reset:
            self.current_minute_count = 0
            self.minute_reset = now + timezone.timedelta(minutes=1)
        
        if self.hour_reset and now > self.hour_reset:
            self.current_hour_count = 0
            self.hour_reset = now + timezone.timedelta(hours=1)
        
        # Check limits
        if self.current_minute_count >= self.requests_per_minute:
            return False
        
        if self.current_hour_count >= self.requests_per_hour:
            return False
        
        return True


class ContentCache(models.Model):
    """
    Cache scraped content to avoid re-scraping
    Improve performance and reduce server load
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=1000, unique=True, db_index=True)
    url_hash = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Content
    raw_content = models.TextField()
    content_type = models.CharField(max_length=100, blank=True)
    content_encoding = models.CharField(max_length=50, blank=True)
    
    # Metadata
    response_headers = JSONField(default=dict, blank=True)
    status_code = models.IntegerField()
    content_length = models.IntegerField(default=0)
    
    # Caching
    cached_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    hit_count = models.IntegerField(default=0)
    
    # Validation
    is_valid = models.BooleanField(default=True)
    validation_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'content_cache'
        ordering = ['-cached_at']
        indexes = [
            models.Index(fields=['expires_at', 'is_valid']),
        ]
    
    def __str__(self):
        return f"Cache: {self.url[:50]}..."
    
    def is_expired(self):
        """Check if cache entry is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
