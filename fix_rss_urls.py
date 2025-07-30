#!/usr/bin/env python3
"""
Update config with correct RSS URLs for competitor blogs
"""

import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Fix RSS URLs
fixes = [
    ("Gong Blog", "https://www.gong.io/blog/rss.xml", "https://www.gong.io/feed"),
    ("Fireflies AI Blog", "https://fireflies.ai/blog/rss.xml", "https://fireflies.ai/blog/feed"),
]

# Apply fixes
for source in config['web_sources']:
    for old_name, old_url, new_url in fixes:
        if source['name'] == old_name and source['url'] == old_url:
            source['url'] = new_url
            print(f"Fixed {old_name}: {old_url} -> {new_url}")

# Remove non-working RSS sources
working_sources = []
for source in config['web_sources']:
    # Keep if it's a major news site or if we've confirmed it works
    keep = True
    non_working = [
        "https://blog.chorusai.co/rss.xml",
        "https://www.mindtickle.com/company/blog/rss.xml", 
        "https://www.phoneburner.com/blog/rss.xml",
        "https://www.cloudtalk.io/blog/rss.xml",
        "https://www.ringover.com/blog/rss.xml",
        "https://www.people.ai/blog/rss.xml"
    ]
    
    if source['url'] in non_working:
        print(f"Removing non-working source: {source['name']}")
        keep = False
    
    if keep:
        working_sources.append(source)

config['web_sources'] = working_sources

# Add some alternative sources that might have more competitor content
new_sources = [
    {
        "name": "VoIP Review",
        "url": "https://www.voipreview.org/feed",
        "type": "rss",
        "enabled": True,
        "keywords": ["voip", "business phone", "cloud calling", "telephony", "communication"]
    },
    {
        "name": "CallCenterTimes",
        "url": "https://www.callcentertimes.com/feed",
        "type": "rss", 
        "enabled": True,
        "keywords": ["call center", "contact center", "customer service", "voice technology"]
    }
]

for source in new_sources:
    config['web_sources'].append(source)
    print(f"Added new source: {source['name']}")

# Save updated config
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"\nConfig updated!")
print(f"Total RSS sources: {len(config['web_sources'])}")
print(f"Total Twitter handles: {len(config['twitter_usernames'])}")