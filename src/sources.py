"""
Data source handlers for web scraping and social media monitoring
"""

import asyncio
import aiohttp
import feedparser
import tweepy
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

class ContentItem:
    def __init__(self, title: str, content: str, url: str, source: str, published: datetime, category: str = None):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published = published
        self.category = category
        self.relevance_score = 0.0
        self.summary = ""
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "published": self.published.isoformat(),
            "category": self.category,
            "relevance_score": self.relevance_score,
            "summary": self.summary
        }

class WebSourceHandler:
    def __init__(self, session: aiohttp.ClientSession, logger):
        self.session = session
        self.logger = logger
    
    async def fetch_rss_feed(self, source_config: Dict, since: datetime) -> List[ContentItem]:
        """Fetch content from RSS feed"""
        try:
            async with self.session.get(source_config["url"]) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch RSS feed {source_config['url']}: {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                items = []
                for entry in feed.entries[:source_config.get("max_items", 50)]:
                    # Parse publication date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    # Skip items older than since date
                    # Make both datetimes timezone-naive for comparison
                    published_naive = published.replace(tzinfo=None) if published.tzinfo else published
                    since_naive = since.replace(tzinfo=None) if since.tzinfo else since
                    if published_naive < since_naive:
                        continue
                    
                    # Extract content
                    content_text = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
                    
                    item = ContentItem(
                        title=entry.title,
                        content=content_text,
                        url=entry.link,
                        source=source_config["name"],
                        published=published
                    )
                    items.append(item)
                
                self.logger.info(f"Fetched {len(items)} items from {source_config['name']}")
                return items
                
        except Exception as e:
            self.logger.error(f"Error fetching RSS feed {source_config['url']}: {str(e)}")
            return []
    
    async def fetch_web_page(self, source_config: Dict, since: datetime) -> List[ContentItem]:
        """Fetch content from web page"""
        try:
            async with self.session.get(source_config["url"]) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch web page {source_config['url']}: {response.status}")
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract articles based on common patterns
                articles = []
                for article in soup.find_all(['article', 'div'], class_=re.compile(r'(article|post|news|story)')):
                    title_elem = article.find(['h1', 'h2', 'h3'], class_=re.compile(r'(title|headline)'))
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    
                    # Find link
                    link_elem = article.find('a', href=True)
                    url = link_elem['href'] if link_elem else source_config["url"]
                    if url.startswith('/'):
                        url = f"{source_config['url'].rstrip('/')}{url}"
                    
                    # Extract content
                    content_elem = article.find(['p', 'div'], class_=re.compile(r'(content|summary|excerpt)'))
                    content_text = content_elem.get_text().strip() if content_elem else ""
                    
                    item = ContentItem(
                        title=title,
                        content=content_text,
                        url=url,
                        source=source_config["name"],
                        published=datetime.now()
                    )
                    articles.append(item)
                
                self.logger.info(f"Fetched {len(articles)} articles from {source_config['name']}")
                return articles[:source_config.get("max_items", 50)]
                
        except Exception as e:
            self.logger.error(f"Error fetching web page {source_config['url']}: {str(e)}")
            return []

class TwitterHandler:
    def __init__(self, bearer_token: str, logger):
        self.logger = logger
        self.client = None
        if bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=bearer_token)
            except Exception as e:
                self.logger.error(f"Failed to initialize Twitter client: {str(e)}")
    
    async def fetch_user_tweets(self, username: str, since: datetime) -> List[ContentItem]:
        """Fetch tweets from a specific user"""
        if not self.client:
            self.logger.warning("Twitter client not initialized")
            return []
        
        try:
            # Get user by username
            user_response = self.client.get_user(username=username)
            if not user_response.data:
                self.logger.warning(f"User @{username} not found")
                return []
            
            user_id = user_response.data.id
            
            # Fetch tweets from the past week (or since last run if longer)
            # For weekly digest, always look back at least 7 days
            week_ago = datetime.now() - timedelta(days=7)
            search_since = min(since, week_ago)  # Use whichever is further back
            
            tweets_response = self.client.get_users_tweets(
                user_id,
                max_results=10,  # Increased back to 10 for weekly coverage
                tweet_fields=['created_at', 'public_metrics'],  # Include metrics for relevance
                start_time=search_since.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                exclude=['retweets', 'replies']  # Exclude retweets and replies for cleaner content
            )
            
            if not tweets_response.data:
                return []
            
            items = []
            for tweet in tweets_response.data:
                # Skip retweets
                if tweet.text.startswith('RT @'):
                    continue
                
                item = ContentItem(
                    title=f"@{username} tweet",
                    content=tweet.text,
                    url=f"https://twitter.com/{username}/status/{tweet.id}",
                    source=f"Twitter @{username}",
                    published=tweet.created_at
                )
                items.append(item)
            
            self.logger.info(f"Fetched {len(items)} tweets from @{username}")
            return items
            
        except Exception as e:
            self.logger.error(f"Error fetching tweets from @{username}: {str(e)}")
            return []

class SourceManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.web_handler = None
        self.twitter_handler = TwitterHandler(config.twitter_bearer_token, logger)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.web_handler = WebSourceHandler(self.session, self.logger)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def fetch_all_content(self, since: datetime) -> List[ContentItem]:
        """Fetch content from all configured sources"""
        all_items = []
        
        # Fetch from web sources
        for source in self.config.web_sources:
            if not source.enabled:
                continue
            
            try:
                if source.type == "rss":
                    items = await self.web_handler.fetch_rss_feed(source.dict(), since)
                elif source.type == "web":
                    items = await self.web_handler.fetch_web_page(source.dict(), since)
                else:
                    self.logger.warning(f"Unknown source type: {source.type}")
                    continue
                
                # Filter by keywords if specified
                if source.keywords:
                    items = self._filter_by_keywords(items, source.keywords)
                
                all_items.extend(items)
                
            except Exception as e:
                self.logger.error(f"Error processing source {source.name}: {str(e)}")
        
        # Fetch from Twitter - fast fail on rate limits (no waiting)
        # FIXED: Do not reset all_items here - it wipes out RSS content!
        
        # Priority competitors only (most important for competitive intelligence)
        priority_accounts = ["aircall", "RingCentral", "dialpad", "8x8", "GongInc", "twilio"]
        accounts_to_try = [acc for acc in priority_accounts if acc in self.config.twitter_usernames]
        
        successful_fetches = 0
        rate_limited = False
        
        self.logger.info(f"🐦 Attempting to fetch from {len(accounts_to_try)} priority Twitter accounts...")
        
        for i, username in enumerate(accounts_to_try[:5]):  # Max 5 attempts
            if rate_limited:
                self.logger.info(f"⚡ Skipping remaining Twitter accounts due to rate limits")
                break
            
            try:
                # Only small delay between successful requests
                if successful_fetches > 0:
                    await asyncio.sleep(1)  # Minimal delay
                
                items = await self.twitter_handler.fetch_user_tweets(username, since)
                if items:
                    all_items.extend(items)
                    successful_fetches += 1
                    self.logger.info(f"✅ @{username}: {len(items)} tweets")
                else:
                    self.logger.info(f"📭 @{username}: No recent tweets")
                
            except Exception as e:
                error_msg = str(e)
                
                # Immediately skip on rate limits - don't waste time
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    self.logger.warning(f"⚡ Hit Twitter rate limits on @{username} - skipping remaining accounts")
                    rate_limited = True
                    break
                
                # Skip on user not found (clean up config later)  
                elif "not found" in error_msg.lower():
                    self.logger.warning(f"👻 @{username} not found - skipping")
                    continue
                
                # For other errors, log and skip remaining (don't waste time)
                else:
                    self.logger.error(f"❌ @{username}: {error_msg}")
                    self.logger.warning(f"⚠️  Twitter error - skipping remaining accounts to save time")
                    break
        
        if successful_fetches > 0:
            self.logger.info(f"Successfully fetched from {successful_fetches} Twitter accounts")
        else:
            self.logger.warning("No Twitter accounts successfully fetched (likely rate limited)")
        
        self.logger.info(f"Total items fetched: {len(all_items)}")
        return all_items
    
    def _filter_by_keywords(self, items: List[ContentItem], keywords: List[str]) -> List[ContentItem]:
        """Filter items by keywords"""
        filtered = []
        for item in items:
            text = f"{item.title} {item.content}".lower()
            if any(keyword.lower() in text for keyword in keywords):
                filtered.append(item)
        return filtered