#!/usr/bin/env python3
"""
Update config.json with additional competitive intelligence sources
"""

import json

# Load current config
with open('config.json', 'r') as f:
    config = json.load(f)

# New RSS sources to add
new_rss_sources = [
    {
        "name": "Gong Blog",
        "url": "https://www.gong.io/blog/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["conversation intelligence", "sales AI", "revenue intelligence", "call analytics", "gong"]
    },
    {
        "name": "Chorus AI Blog", 
        "url": "https://blog.chorusai.co/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["conversation intelligence", "revenue intelligence", "sales AI", "call coaching", "chorus"]
    },
    {
        "name": "MindTickle Blog",
        "url": "https://www.mindtickle.com/company/blog/rss.xml",
        "type": "rss", 
        "enabled": True,
        "keywords": ["sales enablement", "sales coaching", "revenue enablement", "sales training", "mindtickle"]
    },
    {
        "name": "PhoneBurner Blog",
        "url": "https://www.phoneburner.com/blog/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["sales dialing", "phone system", "sales automation", "phoneburner", "dialer"]
    },
    {
        "name": "CloudTalk Blog",
        "url": "https://www.cloudtalk.io/blog/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["cloud telephony", "business phone", "call center", "cloudtalk", "voip"]
    },
    {
        "name": "Ringover Blog",
        "url": "https://www.ringover.com/blog/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["business communications", "cloud phone", "ringover", "unified communications"]
    },
    {
        "name": "Fireflies AI Blog",
        "url": "https://fireflies.ai/blog/rss.xml",
        "type": "rss",
        "enabled": True,
        "keywords": ["conversation intelligence", "meeting AI", "voice AI", "call recording", "fireflies"]
    },
    {
        "name": "People AI Blog",
        "url": "https://www.people.ai/blog/rss.xml", 
        "type": "rss",
        "enabled": True,
        "keywords": ["revenue intelligence", "sales AI", "CRM automation", "sales analytics", "people.ai"]
    },
    {
        "name": "Crayon Blog",
        "url": "https://www.crayon.co/blog/rss.xml",
        "type": "rss", 
        "enabled": True,
        "keywords": ["competitive intelligence", "market intelligence", "competitor tracking", "sales enablement", "crayon"]
    }
]

# New Twitter usernames to add (check for duplicates)
new_twitter_handles = [
    "GongInc", "ChorusAI", "fathom_video", "MindTickle", "nooks_ai",
    "PhoneBurner", "KoncertEngage", "trellus_ai", "PowerDialerAI",
    "ringover_app", "Dialer360", "CallHubIO", "ConnectAndSell", 
    "fireflies_ai", "ReplayzHQ", "people_ai", "salesflare",
    "AcuitySales", "OlivAI", "LevelEleven", "crayon_co",
    "aircoverai", "SaleskenAI", "MaximusAI", "OutscaleAI",
    "CluelyAI", "PlaybookAI", "Profimatix", "OptimixAI"
]

# Add new RSS sources
for source in new_rss_sources:
    # Check if already exists
    existing = False
    for existing_source in config['web_sources']:
        if existing_source['name'] == source['name'] or existing_source['url'] == source['url']:
            existing = True
            break
    if not existing:
        config['web_sources'].append(source)
        print(f"Added RSS source: {source['name']}")

# Add new Twitter handles
for handle in new_twitter_handles:
    if handle not in config['twitter_usernames']:
        config['twitter_usernames'].append(handle)
        print(f"Added Twitter handle: @{handle}")

# Save updated config
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"\nConfig updated!")
print(f"Total RSS sources: {len(config['web_sources'])}")
print(f"Total Twitter handles: {len(config['twitter_usernames'])}")