"""
Configuration management for the AI Competitive Intelligence Agent
"""

import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class SourceConfig(BaseModel):
    name: str
    url: str
    type: str = "rss"  # rss, web, twitter
    enabled: bool = True
    keywords: List[str] = []

class CategoryConfig(BaseModel):
    name: str
    keywords: List[str]
    priority: int = 1  # 1=high, 2=medium, 3=low

class Config(BaseModel):
    # API Keys
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    twitter_bearer_token: str = Field(default_factory=lambda: os.getenv("TWITTER_BEARER_TOKEN", ""))
    
    # Sources
    web_sources: List[SourceConfig] = []
    twitter_usernames: List[str] = []
    
    # Content categories
    categories: List[CategoryConfig] = []
    
    # Processing settings
    max_items_per_source: int = 50
    relevance_threshold: float = 0.6
    summary_max_length: int = 300
    
    # Scheduling
    run_interval_hours: int = 24
    
    # Output settings
    output_format: str = "html"
    email_recipients: List[str] = []
    
    # State management
    state_file: str = "agent_state.json"
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.dict(), f, indent=2)

# Default configuration
DEFAULT_CONFIG = {
    "web_sources": [
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "type": "rss",
            "keywords": ["AI", "voice", "conversational", "sales", "support", "CRM"]
        },
        {
            "name": "VentureBeat",
            "url": "https://venturebeat.com/feed/",
            "type": "rss",
            "keywords": ["artificial intelligence", "voice technology", "sales automation"]
        },
        {
            "name": "The Verge",
            "url": "https://www.theverge.com/rss/index.xml",
            "type": "rss",
            "keywords": ["AI", "voice assistant", "communication"]
        }
    ],
    "twitter_usernames": [
        "aircall",
        "salesforce",
        "hubspot",
        "openai",
        "AnthropicAI",
        "GoogleAI"
    ],
    "categories": [
        {
            "name": "Competitor Intelligence",
            "keywords": ["aircall", "competitor", "funding", "acquisition", "partnership"],
            "priority": 1
        },
        {
            "name": "AI Voice Technology",
            "keywords": ["voice AI", "conversational AI", "voice assistant", "speech recognition"],
            "priority": 1
        },
        {
            "name": "Sales & Support Tech",
            "keywords": ["sales automation", "support automation", "CRM", "customer intelligence"],
            "priority": 2
        },
        {
            "name": "Industry News",
            "keywords": ["telecommunications", "SaaS", "business communication"],
            "priority": 3
        }
    ],
    "max_items_per_source": 50,
    "relevance_threshold": 0.6,
    "summary_max_length": 300,
    "run_interval_hours": 24,
    "output_format": "html",
    "email_recipients": []
}