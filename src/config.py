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
    type: str = "rss"
    enabled: bool = True
    keywords: List[str] = []

class CategoryConfig(BaseModel):
    name: str
    keywords: List[str]
    priority: int = 1

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
    relevance_threshold: float = 0.02
    summary_max_length: int = 300
    
    # Scheduling
    run_interval_hours: int = 24
    
    # Output settings
    output_format: str = "html"
    email_recipients: List[str] = []
    
    # State management
    state_file: str = "agent_state.json"
    
    @classmethod
    def from_file(cls, config_path: str = "config.json"):
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert web_sources to SourceConfig objects
        web_sources = [SourceConfig(**source) for source in config_data.get('web_sources', [])]
        
        # Convert categories to CategoryConfig objects  
        categories = [CategoryConfig(**cat) for cat in config_data.get('categories', [])]
        
        # Create Config instance with JSON values
        return cls(
            web_sources=web_sources,
            twitter_usernames=config_data.get('twitter_usernames', []),
            categories=categories,
            max_items_per_source=config_data.get('max_items_per_source', 50),
            relevance_threshold=config_data.get('relevance_threshold', 0.02),
            summary_max_length=config_data.get('summary_max_length', 300),
            run_interval_hours=config_data.get('run_interval_hours', 24),
            output_format=config_data.get('output_format', 'html'),
            email_recipients=config_data.get('email_recipients', []),
            state_file=config_data.get('state_file', 'agent_state.json')
        )
