#!/usr/bin/env python
"""
Test AI API connections (Novita.ai and Groq)
Verify that the AI services are properly configured and accessible
"""

import os
import asyncio
import httpx
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholarship_hunter.settings')
import django
django.setup()

async def test_novita_api():
    """Test Novita.ai API connection"""
    print("🤖 Testing Novita.ai API connection...")
    
    try:
        api_key = settings.NOVITA_API_KEY
        base_url = settings.NOVITA_BASE_URL
        
        if not api_key or api_key.startswith('sk_c6BRtIxfIVnqkM5TpCPAvo7dmiacZpmj3Boab4DhASg'):
            print("✅ Novita.ai API key found:", api_key[:20] + "..." if len(api_key) > 20 else api_key)
        else:
            print("❌ Novita.ai API key not configured properly")
            return False
        
        # Test API call
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simple test message
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "Hello! Can you help me find scholarships for Tunisia students?"}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print(f"📡 Making test request to {base_url}/openai/chat/completions")
            response = await client.post(
                f"{base_url}/openai/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
                print("✅ Novita.ai API connection successful!")
                print(f"🤖 AI Response: {ai_response[:100]}...")
                return True
            else:
                print(f"❌ Novita.ai API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Novita.ai API connection failed: {str(e)}")
        return False

async def test_groq_api():
    """Test Groq API connection"""
    print("\n🚀 Testing Groq API connection...")
    
    try:
        api_key = settings.GROQ_API_KEY
        
        if not api_key or not api_key.startswith('gsk_'):
            print("❌ Groq API key not configured properly")
            return False
        
        print("✅ Groq API key found:", api_key[:20] + "...")
        
        # Test API call
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simple test message
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "user", "content": "Hello! Can you help me analyze scholarship opportunities?"}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print("📡 Making test request to https://api.groq.com/openai/v1/chat/completions")
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
                print("✅ Groq API connection successful!")
                print(f"🤖 AI Response: {ai_response[:100]}...")
                return True
            else:
                print(f"❌ Groq API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Groq API connection failed: {str(e)}")
        return False

async def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing Neon PostgreSQL database connection...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Test basic connection
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            print(f"✅ Database connected: {db_version}")
            
            # Test scholarship data
            cursor.execute("SELECT COUNT(*) FROM scholarships")
            scholarship_count = cursor.fetchone()[0]
            print(f"✅ Scholarships in database: {scholarship_count}")
            
            # Test Tunisia eligible scholarships
            cursor.execute("SELECT COUNT(*) FROM scholarships WHERE tunisia_eligible = true")
            tunisia_count = cursor.fetchone()[0]
            print(f"✅ Tunisia eligible scholarships: {tunisia_count}")
            
            # Test recent scholarships
            cursor.execute("SELECT name, provider, country FROM scholarships WHERE tunisia_eligible = true LIMIT 3")
            recent = cursor.fetchall()
            print("✅ Sample Tunisia-eligible scholarships:")
            for name, provider, country in recent:
                print(f"   - {name} ({provider}, {country})")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

async def main():
    """Run all connection tests"""
    print("🔧 AI Scholarship Hunter - Connection Tests")
    print("=" * 50)
    
    # Test database
    db_success = await test_database_connection()
    
    # Test AI APIs
    novita_success = await test_novita_api()
    groq_success = await test_groq_api()
    
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST RESULTS:")
    print(f"🗄️ Neon Database: {'✅ Connected' if db_success else '❌ Failed'}")
    print(f"🤖 Novita.ai API: {'✅ Connected' if novita_success else '❌ Failed'}")
    print(f"🚀 Groq API: {'✅ Connected' if groq_success else '❌ Failed'}")
    
    if all([db_success, novita_success, groq_success]):
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("The AI Scholarship Hunter is ready to discover scholarships!")
    else:
        print("\n⚠️ Some connections failed. Please check your configuration.")
    
    return all([db_success, novita_success, groq_success])

if __name__ == "__main__":
    asyncio.run(main())
