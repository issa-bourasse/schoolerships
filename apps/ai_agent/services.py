"""
AI Agent Services

Integration with Novita.ai API for advanced AI models
Autonomous decision-making and content analysis
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
import httpx
from django.conf import settings
from django.utils import timezone
from .models import AIAgent, AIDecision, AIThought, PerformanceMetric
import logging

logger = logging.getLogger(__name__)


class NovitaAIService:
    """
    Service for interacting with Novita.ai API
    Supports multiple AI models including DeepSeek
    """
    
    def __init__(self):
        self.api_key = settings.NOVITA_API_KEY
        self.base_url = settings.NOVITA_BASE_URL
        self.client = None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek/deepseek-v3-0324",  # Most advanced model available
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Novita.ai API
        """
        try:
            # Create client if not exists
            if not self.client:
                self.client = httpx.AsyncClient(
                    timeout=60.0,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                )

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }

            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}{settings.NOVITA_CHAT_ENDPOINT}",
                json=payload
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result['processing_time'] = processing_time
                return result
            else:
                logger.error(f"Novita.ai API error: {response.status_code} - {response.text}")
                return {
                    'error': f"API error: {response.status_code}",
                    'processing_time': processing_time
                }
                
        except Exception as e:
            logger.error(f"Novita.ai API exception: {str(e)}")
            return {
                'error': str(e),
                'processing_time': 0
            }
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None


class ScholarshipHunterAI:
    """
    Main AI agent for autonomous scholarship hunting
    Coordinates multiple specialized agents
    """
    
    def __init__(self, agent_name: str = "Master Scholarship Hunter"):
        self.agent_name = agent_name
        self.novita_service = NovitaAIService()
        self.agent = None
        self.system_prompt = """
You are an advanced AI agent specialized in finding fully-funded scholarships for students from Tunisia.
Your mission is to autonomously search the web, discover new scholarship opportunities, and analyze their relevance.

Key objectives:
1. Find 10,000+ fully-funded scholarships
2. Verify Tunisia eligibility for each scholarship
3. Focus on AI, Web Development, IT, and Computer Science fields
4. Discover new websites and sources autonomously
5. Make strategic decisions about search priorities
6. Analyze content for scholarship relevance
7. Request help when needed

You have access to web scraping tools, content analysis capabilities, and can make autonomous decisions.
Always think step by step and explain your reasoning.
"""
    
    async def initialize_agent(self):
        """Initialize or get existing AI agent"""
        from django.db import transaction
        
        try:
            async with transaction.atomic():
                self.agent, created = await AIAgent.objects.aget_or_create(
                    name=self.agent_name,
                    defaults={
                        'agent_type': 'master',
                        'ai_model': 'deepseek/deepseek-v3-0324',  # Most advanced model
                        'model_provider': 'novita',
                        'system_prompt': self.system_prompt,
                        'is_active': True,
                        'capabilities': {
                            'web_search': True,
                            'content_analysis': True,
                            'decision_making': True,
                            'strategy_planning': True,
                            'tunisia_verification': True
                        }
                    }
                )
                
                if created:
                    logger.info(f"Created new AI agent: {self.agent_name}")
                else:
                    logger.info(f"Using existing AI agent: {self.agent_name}")
                    
                return self.agent
                
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    async def think(self, thought_content: str, thought_type: str = "planning", importance: str = "medium") -> AIThought:
        """
        Record AI agent thinking process
        Make thoughts visible to users in real-time
        """
        try:
            thought = await AIThought.objects.acreate(
                agent=self.agent,
                thought_type=thought_type,
                content=thought_content,
                importance=importance,
                confidence=0.8
            )
            
            # Send real-time update
            await self.broadcast_thinking(thought)
            
            logger.info(f"AI Thought ({thought_type}): {thought_content[:100]}...")
            return thought
            
        except Exception as e:
            logger.error(f"Error recording thought: {str(e)}")
            raise
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        context: str = ""
    ) -> AIDecision:
        """
        Make an autonomous decision using AI
        Record the decision process and reasoning
        """
        try:
            # Prepare messages for AI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""
Make a decision about: {decision_type}

Context: {context}

Input data: {json.dumps(input_data, indent=2)}

Please provide:
1. Your decision
2. Detailed reasoning
3. Confidence score (0-1)
4. Any additional data or recommendations

Respond in JSON format with keys: decision, reasoning, confidence, additional_data
"""}
            ]
            
            # Get AI response
            start_time = time.time()
            response = await self.novita_service.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=2000
            )
            processing_time = time.time() - start_time
            
            if 'error' in response:
                raise Exception(f"AI decision failed: {response['error']}")
            
            # Parse AI response
            ai_content = response['choices'][0]['message']['content']
            
            try:
                decision_data = json.loads(ai_content)
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                decision_data = {
                    'decision': ai_content,
                    'reasoning': 'AI response was not in JSON format',
                    'confidence': 0.5,
                    'additional_data': {}
                }
            
            # Record decision
            decision = await AIDecision.objects.acreate(
                agent=self.agent,
                decision_type=decision_type,
                input_data=input_data,
                output_data=decision_data,
                reasoning=decision_data.get('reasoning', ''),
                confidence_score=decision_data.get('confidence', 0.5),
                processing_time=processing_time,
                tokens_used=response.get('usage', {}).get('total_tokens', 0),
                success=True
            )
            
            # Record performance metric
            await self.record_metric('decision_time', processing_time, 'seconds')
            
            logger.info(f"AI Decision ({decision_type}): {decision_data.get('decision', 'Unknown')}")
            return decision
            
        except Exception as e:
            # Record failed decision
            decision = await AIDecision.objects.acreate(
                agent=self.agent,
                decision_type=decision_type,
                input_data=input_data,
                output_data={},
                reasoning=f"Decision failed: {str(e)}",
                confidence_score=0.0,
                processing_time=time.time() - start_time if 'start_time' in locals() else 0,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"AI Decision failed ({decision_type}): {str(e)}")
            raise
    
    async def analyze_content(self, content: str, url: str, analysis_type: str = "scholarship_detection") -> Dict[str, Any]:
        """
        Analyze web content for scholarship information
        Extract and structure relevant data
        """
        try:
            await self.think(f"Analyzing content from {url} for {analysis_type}", "analysis")
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""
Analyze this web content for scholarship opportunities:

URL: {url}
Analysis Type: {analysis_type}

Content:
{content[:8000]}  # Limit content to avoid token limits

Please extract and analyze:
1. Any scholarship opportunities mentioned
2. Eligibility for Tunisia students
3. Relevance to AI/Web Development/IT fields
4. Application deadlines and requirements
5. Funding information (full/partial)
6. Contact details and application URLs

For each scholarship found, provide structured data including:
- name, provider, country, field_of_study, academic_level
- tunisia_eligible (boolean), funding_type, application_deadline
- application_url, requirements, relevance_scores

Respond in JSON format with a 'scholarships' array and 'analysis_summary'.
"""}
            ]
            
            response = await self.novita_service.chat_completion(
                messages=messages,
                temperature=0.2,  # Low temperature for accurate extraction
                max_tokens=4000
            )
            
            if 'error' in response:
                return {'error': response['error'], 'scholarships': []}
            
            ai_content = response['choices'][0]['message']['content']
            
            try:
                analysis_result = json.loads(ai_content)
                await self.record_metric('content_analysis_success', 1, 'count')
                return analysis_result
            except json.JSONDecodeError:
                await self.record_metric('content_analysis_failure', 1, 'count')
                return {
                    'error': 'Failed to parse AI analysis',
                    'raw_response': ai_content,
                    'scholarships': []
                }
                
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            await self.record_metric('content_analysis_error', 1, 'count')
            return {'error': str(e), 'scholarships': []}
    
    async def plan_search_strategy(self, current_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan next search strategy based on current results
        Autonomous strategic decision-making
        """
        try:
            await self.think("Planning next search strategy based on current results", "planning", "high")
            
            decision = await self.make_decision(
                decision_type="strategy_planning",
                input_data=current_results,
                context="Planning next phase of scholarship search based on current progress"
            )
            
            return decision.output_data
            
        except Exception as e:
            logger.error(f"Strategy planning failed: {str(e)}")
            return {'error': str(e)}
    
    async def record_metric(self, metric_name: str, value: float, unit: str = "", context: Dict = None):
        """Record performance metric"""
        try:
            await PerformanceMetric.objects.acreate(
                agent=self.agent,
                metric_name=metric_name,
                metric_value=value,
                metric_unit=unit,
                context=context or {}
            )
        except Exception as e:
            logger.error(f"Error recording metric: {str(e)}")
    
    async def broadcast_thinking(self, thought: AIThought):
        """Broadcast AI thinking to real-time dashboard"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                await channel_layer.group_send(
                    'dashboard',
                    {
                        'type': 'ai_thinking',
                        'agent': self.agent.name,
                        'thought': {
                            'type': thought.thought_type,
                            'content': thought.content,
                            'importance': thought.importance,
                            'confidence': thought.confidence,
                            'timestamp': thought.created_at.isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting thinking: {str(e)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.novita_service.close()
