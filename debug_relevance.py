#!/usr/bin/env python3
"""
Debug relevance scoring to understand why so few items pass
"""

import asyncio
import sys
import os
sys.path.append('.')

from src.config import Config
from src.logger import Logger
from src.sources import SourceManager
from src.processor import ContentProcessor

async def debug_relevance():
    config = Config()
    logger = Logger().get_logger()
    
    print(f"🔍 Debugging relevance scoring...")
    print(f"Current threshold: {config.relevance_threshold}")
    
    # Fetch a small sample of content
    async with SourceManager(config, logger) as source_manager:
        # Just fetch from a few sources for debugging
        from datetime import datetime, timedelta
        since = datetime.now() - timedelta(days=7)  # Last week
        
        items = []
        
        # Fetch from TechCrunch
        try:
            tc_items = await source_manager._fetch_rss_feed("https://techcrunch.com/feed/", "TechCrunch", since)
            items.extend(tc_items[:5])  # Just 5 items
            print(f"📰 Fetched {len(tc_items)} items from TechCrunch")
        except Exception as e:
            print(f"❌ Failed to fetch TechCrunch: {e}")
        
        # Test relevance scoring
        processor = ContentProcessor(config, logger)
        
        print(f"\n🎯 Testing relevance scoring on {len(items)} items:")
        print("=" * 80)
        
        for i, item in enumerate(items):
            score = processor._calculate_relevance_score(item)
            status = "✅ PASS" if score >= config.relevance_threshold else "❌ FAIL"
            
            print(f"\n{i+1}. {status} (Score: {score:.3f})")
            print(f"   Title: {item.title[:60]}...")
            print(f"   Content preview: {item.content[:80]}...")
            
            # Check critical keywords
            text = f"{item.title} {item.content}".lower()
            
            critical_keywords = [
                "aircall", "ringcentral", "8x8", "dialpad", "vonage", "twilio", "five9", "genesys",
                "cloud phone", "voip", "business phone", "phone system", "call center software",
                "contact center", "cloud calling", "voice api", "telephony",
                "conversation intelligence", "call analytics", "call recording", "call coaching",
                "sales calls", "call transcription", "voice analytics"
            ]
            
            found_critical = []
            for keyword in critical_keywords:
                if processor._enhanced_keyword_match(keyword, text):
                    found_critical.append(keyword)
            
            if found_critical:
                print(f"   🎯 Critical keywords found: {', '.join(found_critical)}")
            else:
                print(f"   ⚠️  No critical keywords found")
                
                # Check phone context
                phone_words = ["phone", "call", "voice", "dial"]
                has_phone = any(word in text for word in phone_words)
                print(f"   📞 Has phone context: {has_phone}")
            
            print(f"   🔗 URL: {item.url}")

if __name__ == "__main__":
    asyncio.run(debug_relevance())