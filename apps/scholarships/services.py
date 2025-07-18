"""
Scholarship Search Services

Main orchestrator for AI-powered scholarship hunting
Coordinates AI agents, web scraping, and data processing
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.conf import settings
from channels.layers import get_channel_layer
from apps.ai_agent.services import ScholarshipHunterAI
from apps.scraper.engines import AsyncWebScraper, ContentExtractor
from .models import Scholarship, SearchSession, WebsiteTarget
import logging

logger = logging.getLogger(__name__)


class ScholarshipSearchOrchestrator:
    """
    Main orchestrator for autonomous scholarship hunting
    Coordinates AI agents, web scraping, and real-time updates
    """
    
    def __init__(self, session_name: str = "AI Scholarship Hunt"):
        self.session_name = session_name
        self.ai_agent = ScholarshipHunterAI()
        self.content_extractor = ContentExtractor()
        self.channel_layer = get_channel_layer()
        self.search_session = None
        self.is_running = False
        
        # Initial target websites (AI will discover more)
        self.seed_websites = [
            "https://www.scholarshipportal.com",
            "https://www.studyportals.com",
            "https://www.scholarships.com",
            "https://www.fastweb.com",
            "https://www.findamasters.com",
            "https://www.phdportal.com",
            "https://ec.europa.eu/programmes/erasmus-plus",
            "https://www.daad.de/en",
            "https://www.chevening.org",
            "https://www.fulbright.org",
            "https://www.britishcouncil.org",
            "https://www.campus-france.org",
            "https://www.australia.gov.au/information-and-services/education-and-training",
            "https://www.canada.ca/en/services/benefits/education",
            "https://www.studyinnorway.no",
            "https://www.studyinsweden.se",
            "https://www.studyindenmark.dk",
            "https://www.studyinfinland.fi",
            "https://www.nuffic.nl",
            "https://www.universitiesaustralia.edu.au"
        ]
    
    async def start_search(self, target_scholarships: int = 10000) -> str:
        """
        Start autonomous scholarship search
        Returns session ID for tracking
        """
        try:
            # Initialize AI agent
            await self.ai_agent.initialize_agent()
            
            # Create search session
            self.search_session = await SearchSession.objects.acreate(
                session_name=self.session_name,
                target_scholarships=target_scholarships,
                status='running',
                ai_model_used='deepseek-chat',
                search_strategy='AI-guided autonomous search'
            )
            
            self.is_running = True
            
            # Start the search process
            asyncio.create_task(self._run_search_loop())
            
            # Broadcast start event
            await self.broadcast_event('search_started', {
                'session_id': str(self.search_session.id),
                'session_name': self.session_name,
                'target_scholarships': target_scholarships
            })
            
            logger.info(f"Started scholarship search session: {self.search_session.id}")
            return str(self.search_session.id)
            
        except Exception as e:
            logger.error(f"Error starting search: {str(e)}")
            raise
    
    async def _run_search_loop(self):
        """
        Main search loop - runs continuously until target is reached
        """
        try:
            await self.ai_agent.think(
                f"Starting autonomous scholarship search for {self.search_session.target_scholarships} scholarships",
                "planning",
                "high"
            )
            
            phase = 1
            websites_discovered = set(self.seed_websites)
            
            while self.is_running and self.search_session.scholarships_found < self.search_session.target_scholarships:
                
                await self.ai_agent.think(f"Starting search phase {phase}", "planning")
                
                # Phase 1: Search seed websites
                if phase == 1:
                    await self._search_seed_websites()
                
                # Phase 2+: AI-guided discovery and search
                else:
                    # Let AI decide next strategy
                    current_stats = await self._get_current_stats()
                    strategy = await self.ai_agent.plan_search_strategy(current_stats)
                    
                    if 'error' not in strategy:
                        await self._execute_ai_strategy(strategy)
                    else:
                        await self.ai_agent.think(
                            f"Strategy planning failed: {strategy['error']}. Using fallback approach.",
                            "reflection",
                            "medium"
                        )
                        await self._fallback_search()
                
                # Update progress
                await self._update_search_progress()
                
                # Check if we should continue
                if await self._should_continue_search():
                    phase += 1
                    await asyncio.sleep(5)  # Brief pause between phases
                else:
                    break
            
            # Complete search
            await self._complete_search()
            
        except Exception as e:
            logger.error(f"Search loop error: {str(e)}")
            await self._handle_search_error(str(e))
    
    async def _search_seed_websites(self):
        """Search initial seed websites"""
        await self.ai_agent.think("Searching seed websites for scholarship opportunities", "analysis")
        
        async with AsyncWebScraper(max_concurrent=5) as scraper:
            
            async def process_result(result, index, total):
                await self.broadcast_progress(f"Searching website {index}/{total}: {result['url']}")
                
                if result['success']:
                    await self._process_scraped_content(result)
                else:
                    logger.warning(f"Failed to scrape {result['url']}: {result.get('error', 'Unknown error')}")
            
            # Scrape seed websites
            results = await scraper.scrape_multiple(
                self.seed_websites,
                session_name=f"seed_search_{self.search_session.id}",
                callback=process_result
            )
            
            # Update websites searched count
            self.search_session.websites_searched += len(results)
            await self.search_session.asave()
    
    async def _process_scraped_content(self, scrape_result: Dict[str, Any]):
        """Process scraped content and extract scholarships"""
        try:
            url = scrape_result['url']
            content = scrape_result['content']
            
            # Extract text content
            extracted = self.content_extractor.extract_text_content(content, url)
            
            # Check for scholarship indicators
            indicators = self.content_extractor.find_scholarship_indicators(extracted['content'], url)
            
            if indicators['likely_scholarship_page']:
                await self.ai_agent.think(
                    f"Found potential scholarship page: {url} (score: {indicators['overall_score']:.2f})",
                    "discovery"
                )
                
                # Use AI to analyze content for scholarships
                analysis = await self.ai_agent.analyze_content(
                    extracted['content'],
                    url,
                    "scholarship_detection"
                )
                
                if 'scholarships' in analysis and analysis['scholarships']:
                    await self._save_scholarships(analysis['scholarships'], url)
                
                # Discover new websites from links
                await self._discover_new_websites(extracted['links'], url)
            
        except Exception as e:
            logger.error(f"Error processing scraped content: {str(e)}")
    
    async def _save_scholarships(self, scholarships: List[Dict], source_url: str):
        """Save discovered scholarships to database"""
        try:
            saved_count = 0
            
            for scholarship_data in scholarships:
                try:
                    # Check if scholarship already exists
                    existing = await Scholarship.objects.filter(
                        name=scholarship_data.get('name', ''),
                        provider=scholarship_data.get('provider', ''),
                        source_url=source_url
                    ).afirst()
                    
                    if not existing:
                        # Create new scholarship
                        scholarship = await Scholarship.objects.acreate(
                            name=scholarship_data.get('name', 'Unknown'),
                            provider=scholarship_data.get('provider', 'Unknown'),
                            country=scholarship_data.get('country', ''),
                            region=scholarship_data.get('region', ''),
                            tunisia_eligible=scholarship_data.get('tunisia_eligible', False),
                            eligible_countries=scholarship_data.get('eligible_countries', []),
                            field_of_study=scholarship_data.get('field_of_study', ''),
                            academic_level=scholarship_data.get('academic_level', 'any'),
                            ai_relevance_score=scholarship_data.get('ai_relevance_score', 0.0),
                            web_dev_relevance_score=scholarship_data.get('web_dev_relevance_score', 0.0),
                            it_relevance_score=scholarship_data.get('it_relevance_score', 0.0),
                            overall_relevance_score=scholarship_data.get('overall_relevance_score', 0.0),
                            funding_type=scholarship_data.get('funding_type', 'full'),
                            funding_amount=scholarship_data.get('funding_amount', ''),
                            funding_coverage=scholarship_data.get('funding_coverage', ''),
                            application_url=scholarship_data.get('application_url', source_url),
                            application_process=scholarship_data.get('application_process', ''),
                            required_documents=scholarship_data.get('required_documents', []),
                            language_requirements=scholarship_data.get('language_requirements', ''),
                            other_requirements=scholarship_data.get('other_requirements', ''),
                            duration=scholarship_data.get('duration', ''),
                            contact_email=scholarship_data.get('contact_email', ''),
                            contact_website=scholarship_data.get('contact_website', ''),
                            source_url=source_url,
                            source_website=source_url.split('/')[2] if '/' in source_url else source_url,
                            is_active=True,
                            ai_processed=True
                        )
                        
                        saved_count += 1
                        
                        # Broadcast scholarship found
                        await self.broadcast_event('scholarship_found', {
                            'scholarship': {
                                'id': str(scholarship.id),
                                'name': scholarship.name,
                                'provider': scholarship.provider,
                                'country': scholarship.country,
                                'tunisia_eligible': scholarship.tunisia_eligible,
                                'funding_type': scholarship.funding_type,
                                'relevance_score': scholarship.overall_relevance_score
                            }
                        })
                
                except Exception as e:
                    logger.error(f"Error saving individual scholarship: {str(e)}")
                    continue
            
            if saved_count > 0:
                # Update session count
                self.search_session.scholarships_found += saved_count
                await self.search_session.asave()
                
                await self.ai_agent.think(
                    f"Saved {saved_count} new scholarships from {source_url}",
                    "discovery",
                    "high"
                )
            
        except Exception as e:
            logger.error(f"Error saving scholarships: {str(e)}")
    
    async def _discover_new_websites(self, links: List[Dict], source_url: str):
        """Discover new websites from extracted links"""
        try:
            scholarship_related_links = []
            
            for link in links:
                link_text = link['text'].lower()
                link_url = link['url']
                
                # Check if link text suggests scholarship content
                if any(keyword in link_text for keyword in [
                    'scholarship', 'grant', 'funding', 'fellowship', 'financial aid',
                    'apply', 'application', 'student', 'education', 'university'
                ]):
                    scholarship_related_links.append(link)
            
            # Let AI decide which links to explore
            if scholarship_related_links:
                decision = await self.ai_agent.make_decision(
                    decision_type="website_discovery",
                    input_data={
                        'source_url': source_url,
                        'potential_links': scholarship_related_links[:10],  # Limit for AI processing
                        'link_count': len(scholarship_related_links)
                    },
                    context="Deciding which discovered links to explore for scholarships"
                )
                
                if decision.success and 'selected_links' in decision.output_data:
                    selected_links = decision.output_data['selected_links']
                    
                    for link_url in selected_links:
                        # Add to website targets
                        await WebsiteTarget.objects.aget_or_create(
                            url=link_url,
                            defaults={
                                'domain': link_url.split('/')[2] if '/' in link_url else link_url,
                                'website_type': 'discovered',
                                'discovered_by_ai': True,
                                'discovery_method': 'link_analysis'
                            }
                        )
        
        except Exception as e:
            logger.error(f"Error discovering new websites: {str(e)}")
    
    async def _get_current_stats(self) -> Dict[str, Any]:
        """Get current search statistics"""
        try:
            total_scholarships = await Scholarship.objects.filter(is_active=True).acount()
            tunisia_scholarships = await Scholarship.objects.filter(
                tunisia_eligible=True,
                is_active=True
            ).acount()
            
            return {
                'total_scholarships': total_scholarships,
                'tunisia_scholarships': tunisia_scholarships,
                'target_scholarships': self.search_session.target_scholarships,
                'websites_searched': self.search_session.websites_searched,
                'session_duration': (timezone.now() - self.search_session.started_at).total_seconds()
            }
        except Exception as e:
            logger.error(f"Error getting current stats: {str(e)}")
            return {}
    
    async def _execute_ai_strategy(self, strategy: Dict[str, Any]):
        """Execute AI-generated search strategy"""
        try:
            await self.ai_agent.think(
                f"Executing AI strategy: {strategy.get('decision', 'Unknown strategy')}",
                "planning"
            )
            
            # This would implement the AI's strategic decisions
            # For now, continue with discovered websites
            await self._search_discovered_websites()
            
        except Exception as e:
            logger.error(f"Error executing AI strategy: {str(e)}")
    
    async def _search_discovered_websites(self):
        """Search websites discovered by AI"""
        try:
            # Get undiscovered websites
            targets = await WebsiteTarget.objects.filter(
                is_active=True,
                last_scraped__isnull=True
            ).order_by('-scholarships_found')[:10]
            
            if targets:
                urls = [target.url async for target in targets]
                
                async with AsyncWebScraper(max_concurrent=3) as scraper:
                    results = await scraper.scrape_multiple(
                        urls,
                        session_name=f"discovered_search_{self.search_session.id}"
                    )
                    
                    for result in results:
                        if result['success']:
                            await self._process_scraped_content(result)
                        
                        # Update website target
                        try:
                            target = await WebsiteTarget.objects.aget(url=result['url'])
                            target.last_scraped = timezone.now()
                            target.scrape_count += 1
                            if result['success']:
                                target.success_count += 1
                            await target.asave()
                        except WebsiteTarget.DoesNotExist:
                            pass
                
                self.search_session.websites_searched += len(results)
                await self.search_session.asave()
        
        except Exception as e:
            logger.error(f"Error searching discovered websites: {str(e)}")
    
    async def _fallback_search(self):
        """Fallback search strategy when AI planning fails"""
        await self.ai_agent.think("Using fallback search strategy", "planning")
        await self._search_discovered_websites()
    
    async def _should_continue_search(self) -> bool:
        """Determine if search should continue"""
        if not self.is_running:
            return False
        
        if self.search_session.scholarships_found >= self.search_session.target_scholarships:
            return False
        
        # Check if we've been running too long (safety limit)
        duration = (timezone.now() - self.search_session.started_at).total_seconds()
        if duration > settings.SEARCH_TIMEOUT:
            await self.ai_agent.think("Search timeout reached, completing search", "reflection")
            return False
        
        return True
    
    async def _update_search_progress(self):
        """Update and broadcast search progress"""
        try:
            progress = {
                'scholarships_found': self.search_session.scholarships_found,
                'target_scholarships': self.search_session.target_scholarships,
                'websites_searched': self.search_session.websites_searched,
                'progress_percentage': min(
                    (self.search_session.scholarships_found / self.search_session.target_scholarships) * 100,
                    100
                )
            }
            
            await self.broadcast_event('search_progress', progress)
            
        except Exception as e:
            logger.error(f"Error updating search progress: {str(e)}")
    
    async def _complete_search(self):
        """Complete the search session"""
        try:
            self.is_running = False
            self.search_session.status = 'completed'
            self.search_session.ended_at = timezone.now()
            await self.search_session.asave()
            
            final_stats = await self._get_current_stats()
            
            await self.ai_agent.think(
                f"Search completed! Found {final_stats['total_scholarships']} total scholarships, "
                f"{final_stats['tunisia_scholarships']} eligible for Tunisia students.",
                "reflection",
                "high"
            )
            
            await self.broadcast_event('search_completed', final_stats)
            
            # Cleanup
            await self.ai_agent.cleanup()
            
        except Exception as e:
            logger.error(f"Error completing search: {str(e)}")
    
    async def _handle_search_error(self, error_message: str):
        """Handle search errors"""
        try:
            self.is_running = False
            self.search_session.status = 'failed'
            self.search_session.error_log = error_message
            self.search_session.ended_at = timezone.now()
            await self.search_session.asave()
            
            await self.broadcast_event('search_error', {'error': error_message})
            
        except Exception as e:
            logger.error(f"Error handling search error: {str(e)}")
    
    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to real-time dashboard"""
        try:
            if self.channel_layer:
                await self.channel_layer.group_send(
                    'dashboard',
                    {
                        'type': 'dashboard_message',
                        'event_type': event_type,
                        'data': data,
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting event: {str(e)}")
    
    async def broadcast_progress(self, message: str):
        """Broadcast progress message"""
        await self.broadcast_event('progress_update', {'message': message})
    
    async def stop_search(self):
        """Stop the current search"""
        self.is_running = False
        await self.ai_agent.think("Search stopped by user request", "reflection")
        await self.broadcast_event('search_stopped', {})
