#!/usr/bin/env python3
"""
Add alternative competitor intelligence sources that don't rely on Twitter API
"""

import json
import asyncio
import aiohttp

async def test_alternative_sources():
    """Test alternative RSS and news sources"""
    
    # Company press release feeds and investor relations
    alternative_sources = [
        # Direct company sources
        ("RingCentral News", "https://investors.ringcentral.com/news-releases/rss"),
        ("RingCentral Press", "https://www.ringcentral.com/news/rss.xml"),
        ("8x8 Press", "https://www.8x8.com/news/press-releases/rss.xml"), 
        ("Twilio News", "https://www.twilio.com/press/rss.xml"),
        ("Zoom Press", "https://blog.zoom.us/feed/"),
        ("Microsoft Teams Blog", "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=news"),
        
        # Industry news sources focused on our space
        ("Contact Center Pipeline", "https://www.contactcenterpipeline.com/rss.xml"),
        ("Enterprise Communications", "https://www.enterprisenetworkingplanet.com/feed/"),
        ("VoIP News", "https://voipnews.com/feed/"),
        ("BCStrategies", "https://www.bcstrategies.com/feed/"),
        
        # Business/funding news that might mention competitors
        ("PitchBook News", "https://pitchbook.com/rss/news"),
        ("Crunchbase Daily", "https://about.crunchbase.com/feed/"),
        ("SaaS News", "https://www.saasify.co/feed/"),
    ]
    
    working_sources = []
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing alternative competitor intelligence sources...")
        print()
        
        for name, url in alternative_sources:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_length = len(content)
                        
                        # Check if it looks like RSS/XML
                        if 'rss' in content.lower() or 'feed' in content.lower() or '<?xml' in content:
                            print(f"✅ {name}")
                            print(f"   URL: {url}")
                            print(f"   Status: {response.status} ({content_length:,} chars)")
                            
                            # Quick check for competitor mentions
                            competitors = ['aircall', 'ringcentral', 'dialpad', 'gong', 'twilio', '8x8', 'zoom']
                            found = [comp for comp in competitors if comp in content.lower()]
                            if found:
                                print(f"   🎯 Contains: {', '.join(found)}")
                            
                            working_sources.append({
                                "name": name,
                                "url": url,
                                "type": "rss",
                                "enabled": True,
                                "keywords": [
                                    "cloud communications", "voip", "contact center", "business phone",
                                    "conversation intelligence", "sales enablement", "AI voice"
                                ]
                            })
                            print()
                        else:
                            print(f"⚠️  {name}: Not RSS/XML format")
                    else:
                        print(f"❌ {name}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
    
    print(f"\n📈 Found {len(working_sources)} working alternative sources")
    return working_sources

async def add_sources_to_config():
    """Add working alternative sources to config"""
    
    # Test sources first
    working_sources = await test_alternative_sources()
    
    if not working_sources:
        print("No working alternative sources found")
        return
    
    # Load current config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Add new sources
    added_count = 0
    for source in working_sources:
        # Check if already exists
        exists = any(existing['url'] == source['url'] for existing in config['web_sources'])
        
        if not exists:
            config['web_sources'].append(source)
            added_count += 1
            print(f"➕ Added: {source['name']}")
    
    if added_count > 0:
        # Save updated config
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Added {added_count} new alternative sources to config")
        print(f"📊 Total RSS sources: {len(config['web_sources'])}")
        print(f"📊 Total Twitter handles: {len(config['twitter_usernames'])}")
    else:
        print("\n📋 No new sources to add (all already exist)")

if __name__ == "__main__":
    asyncio.run(add_sources_to_config())