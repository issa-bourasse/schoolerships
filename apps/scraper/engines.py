"""
Web Scraping Engines

Async web scraping with multiple strategies
AI-guided content extraction and analysis
"""

import asyncio
import aiohttp
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from django.conf import settings
from django.utils import timezone
from .models import ScrapingSession, ProxyServer, RateLimitTracker, ContentCache, ScrapingRule
import logging

logger = logging.getLogger(__name__)


class AsyncWebScraper:
    """
    High-performance async web scraper
    Handles rate limiting, proxy rotation, and content caching
    """
    
    def __init__(self, max_concurrent: int = None):
        self.max_concurrent = max_concurrent or settings.MAX_CONCURRENT_REQUESTS
        self.user_agent = UserAgent()
        self.session = None
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_url(
        self,
        url: str,
        session_name: str = "default",
        use_cache: bool = True,
        follow_redirects: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape a single URL with full error handling and caching
        """
        async with self.semaphore:
            scraping_session = None
            start_time = time.time()
            
            try:
                # Create scraping session record
                scraping_session = await ScrapingSession.objects.acreate(
                    session_name=session_name,
                    target_url=url,
                    scraper_type='aiohttp',
                    user_agent=self.user_agent.random
                )
                
                # Check rate limiting
                domain = urlparse(url).netloc
                if not await self.can_make_request(domain):
                    await self.update_session_status(scraping_session, 'failed', 'Rate limited')
                    return {
                        'success': False,
                        'error': 'Rate limited',
                        'url': url,
                        'session_id': str(scraping_session.id)
                    }
                
                # Check cache first
                if use_cache:
                    cached_content = await self.get_cached_content(url)
                    if cached_content:
                        await self.update_session_status(scraping_session, 'completed', 'From cache')
                        return {
                            'success': True,
                            'content': cached_content['content'],
                            'url': url,
                            'from_cache': True,
                            'session_id': str(scraping_session.id)
                        }
                
                # Make HTTP request
                proxy = await self.get_proxy(domain)
                
                async with self.session.get(
                    url,
                    proxy=proxy,
                    allow_redirects=follow_redirects,
                    headers={'User-Agent': self.user_agent.random}
                ) as response:
                    
                    # Update rate limiting
                    await self.update_rate_limit(domain)
                    
                    # Check response
                    if response.status == 200:
                        content = await response.text()
                        
                        # Cache content
                        if use_cache:
                            await self.cache_content(url, content, response.status, dict(response.headers))
                        
                        # Update session
                        duration = time.time() - start_time
                        await self.update_session_success(scraping_session, content, response.status, duration)
                        
                        return {
                            'success': True,
                            'content': content,
                            'url': url,
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'from_cache': False,
                            'session_id': str(scraping_session.id)
                        }
                    
                    else:
                        error_msg = f"HTTP {response.status}"
                        await self.update_session_status(scraping_session, 'failed', error_msg)
                        return {
                            'success': False,
                            'error': error_msg,
                            'url': url,
                            'status_code': response.status,
                            'session_id': str(scraping_session.id)
                        }
            
            except asyncio.TimeoutError:
                await self.update_session_status(scraping_session, 'timeout', 'Request timeout')
                return {
                    'success': False,
                    'error': 'Request timeout',
                    'url': url,
                    'session_id': str(scraping_session.id) if scraping_session else None
                }
            
            except Exception as e:
                error_msg = str(e)
                if scraping_session:
                    await self.update_session_status(scraping_session, 'failed', error_msg)
                
                logger.error(f"Scraping error for {url}: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'url': url,
                    'session_id': str(scraping_session.id) if scraping_session else None
                }
    
    async def scrape_multiple(
        self,
        urls: List[str],
        session_name: str = "batch",
        callback=None
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently
        """
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.scrape_url(url, session_name))
            tasks.append(task)
        
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            
            # Call callback if provided
            if callback:
                await callback(result, i + 1, len(urls))
        
        return results
    
    async def can_make_request(self, domain: str) -> bool:
        """Check if we can make a request to this domain"""
        try:
            tracker, created = await RateLimitTracker.objects.aget_or_create(
                domain=domain,
                defaults={
                    'requests_per_minute': 10,
                    'requests_per_hour': 100
                }
            )
            
            return tracker.can_make_request()
        except Exception as e:
            logger.error(f"Error checking rate limit for {domain}: {str(e)}")
            return True  # Allow request if check fails
    
    async def update_rate_limit(self, domain: str):
        """Update rate limiting counters"""
        try:
            tracker, created = await RateLimitTracker.objects.aget_or_create(
                domain=domain,
                defaults={
                    'requests_per_minute': 10,
                    'requests_per_hour': 100
                }
            )
            
            now = timezone.now()
            
            # Initialize reset times if needed
            if not tracker.minute_reset:
                tracker.minute_reset = now + timezone.timedelta(minutes=1)
            if not tracker.hour_reset:
                tracker.hour_reset = now + timezone.timedelta(hours=1)
            
            # Reset counters if needed
            if now > tracker.minute_reset:
                tracker.current_minute_count = 0
                tracker.minute_reset = now + timezone.timedelta(minutes=1)
            
            if now > tracker.hour_reset:
                tracker.current_hour_count = 0
                tracker.hour_reset = now + timezone.timedelta(hours=1)
            
            # Increment counters
            tracker.current_minute_count += 1
            tracker.current_hour_count += 1
            tracker.last_request = now
            
            await tracker.asave()
            
        except Exception as e:
            logger.error(f"Error updating rate limit for {domain}: {str(e)}")
    
    async def get_proxy(self, domain: str) -> Optional[str]:
        """Get proxy for domain if needed"""
        if not settings.PROXY_ENABLED:
            return None
        
        try:
            # Get active proxy that's not blocked for this domain
            proxy = await ProxyServer.objects.filter(
                is_active=True,
                is_blocked=False
            ).exclude(
                blocked_websites__contains=[domain]
            ).order_by('?').afirst()
            
            if proxy:
                proxy_url = f"{proxy.proxy_type}://"
                if proxy.username and proxy.password:
                    proxy_url += f"{proxy.username}:{proxy.password}@"
                proxy_url += f"{proxy.host}:{proxy.port}"
                return proxy_url
            
        except Exception as e:
            logger.error(f"Error getting proxy for {domain}: {str(e)}")
        
        return None
    
    async def get_cached_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached content if available and not expired"""
        try:
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            cache_entry = await ContentCache.objects.filter(
                url_hash=url_hash,
                is_valid=True
            ).afirst()
            
            if cache_entry and not cache_entry.is_expired():
                # Update hit count
                cache_entry.hit_count += 1
                await cache_entry.asave()
                
                return {
                    'content': cache_entry.raw_content,
                    'status_code': cache_entry.status_code,
                    'headers': cache_entry.response_headers
                }
        
        except Exception as e:
            logger.error(f"Error getting cached content for {url}: {str(e)}")
        
        return None
    
    async def cache_content(
        self,
        url: str,
        content: str,
        status_code: int,
        headers: Dict[str, str],
        cache_duration_hours: int = 24
    ):
        """Cache content for future use"""
        try:
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            expires_at = timezone.now() + timezone.timedelta(hours=cache_duration_hours)
            
            await ContentCache.objects.aupdate_or_create(
                url_hash=url_hash,
                defaults={
                    'url': url,
                    'raw_content': content,
                    'status_code': status_code,
                    'response_headers': headers,
                    'content_length': len(content),
                    'expires_at': expires_at,
                    'is_valid': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error caching content for {url}: {str(e)}")
    
    async def update_session_status(self, session: ScrapingSession, status: str, error_msg: str = ""):
        """Update scraping session status"""
        try:
            session.status = status
            session.ended_at = timezone.now()
            session.duration_seconds = (session.ended_at - session.started_at).total_seconds()
            if error_msg:
                session.error_message = error_msg
            await session.asave()
        except Exception as e:
            logger.error(f"Error updating session status: {str(e)}")
    
    async def update_session_success(
        self,
        session: ScrapingSession,
        content: str,
        status_code: int,
        duration: float
    ):
        """Update session with successful result"""
        try:
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.duration_seconds = duration
            session.response_code = status_code
            session.response_size = len(content)
            session.pages_scraped = 1
            await session.asave()
        except Exception as e:
            logger.error(f"Error updating session success: {str(e)}")


class ContentExtractor:
    """
    Extract structured data from web content
    AI-guided extraction with fallback rules
    """
    
    def __init__(self):
        self.common_selectors = {
            'title': ['h1', 'title', '.title', '#title'],
            'content': ['.content', '#content', 'main', 'article'],
            'links': ['a[href]'],
            'scholarships': [
                '.scholarship',
                '.grant',
                '.funding',
                '[class*="scholarship"]',
                '[class*="grant"]',
                '[class*="funding"]'
            ]
        }
    
    def extract_text_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract clean text content from HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract main content
            content = ""
            for selector in self.common_selectors['content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # Fallback to body text
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and text:
                    absolute_url = urljoin(url, href)
                    links.append({
                        'url': absolute_url,
                        'text': text,
                        'is_external': urlparse(absolute_url).netloc != urlparse(url).netloc
                    })
            
            return {
                'title': title,
                'content': content,
                'links': links,
                'word_count': len(content.split()) if content else 0,
                'link_count': len(links)
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'title': "",
                'content': "",
                'links': [],
                'word_count': 0,
                'link_count': 0,
                'error': str(e)
            }
    
    def find_scholarship_indicators(self, content: str, url: str) -> Dict[str, Any]:
        """Find indicators that suggest scholarship content"""
        scholarship_keywords = [
            'scholarship', 'grant', 'funding', 'fellowship', 'bursary',
            'financial aid', 'tuition', 'stipend', 'award', 'prize',
            'fully funded', 'full funding', 'free tuition', 'no cost',
            'application deadline', 'apply now', 'eligibility',
            'international students', 'tunisia', 'north africa'
        ]
        
        field_keywords = [
            'computer science', 'artificial intelligence', 'machine learning',
            'web development', 'software engineering', 'information technology',
            'cybersecurity', 'data science', 'programming', 'coding'
        ]
        
        content_lower = content.lower()
        
        # Count keyword matches
        scholarship_matches = sum(1 for keyword in scholarship_keywords if keyword in content_lower)
        field_matches = sum(1 for keyword in field_keywords if keyword in content_lower)
        
        # Calculate relevance scores
        scholarship_score = min(scholarship_matches / len(scholarship_keywords), 1.0)
        field_score = min(field_matches / len(field_keywords), 1.0)
        
        return {
            'scholarship_score': scholarship_score,
            'field_score': field_score,
            'overall_score': (scholarship_score + field_score) / 2,
            'scholarship_matches': scholarship_matches,
            'field_matches': field_matches,
            'likely_scholarship_page': scholarship_score > 0.1 and field_score > 0.05
        }
