"""
Advanced Twitter rate limit optimization strategies
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import tweepy

class TwitterQuotaManager:
    """Intelligent Twitter API quota management"""
    
    def __init__(self, bearer_token: str, logger):
        self.bearer_token = bearer_token
        self.logger = logger
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.quota_state_file = "twitter_quota_state.json"
        
    def load_quota_state(self) -> Dict:
        """Load quota usage state from file"""
        try:
            with open(self.quota_state_file, 'r') as f:
                state = json.load(f)
                # Reset if it's a new month
                last_reset = datetime.fromisoformat(state.get('last_reset', '2000-01-01'))
                if last_reset.month != datetime.now().month:
                    return self._reset_quota_state()
                return state
        except:
            return self._reset_quota_state()
    
    def save_quota_state(self, state: Dict):
        """Save quota usage state to file"""
        with open(self.quota_state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _reset_quota_state(self) -> Dict:
        """Reset quota state for new month"""
        return {
            'last_reset': datetime.now().isoformat(),
            'tweets_fetched': 0,
            'daily_usage': {},
            'account_priority': {},
            'rate_limit_windows': []
        }
    
    async def get_optimal_fetch_plan(self, accounts: List[str], days_back: int = 7) -> Dict:
        """Create optimal fetching plan based on available quota"""
        state = self.load_quota_state()
        
        # Estimate available quota
        monthly_limit = self._get_monthly_limit()
        used_quota = state.get('tweets_fetched', 0)
        available_quota = monthly_limit - used_quota
        
        self.logger.info(f"📊 Twitter Quota: {used_quota}/{monthly_limit} used ({available_quota} remaining)")
        
        # Prioritize accounts based on competitive importance
        prioritized_accounts = self._prioritize_accounts(accounts, state)
        
        # Calculate optimal fetch strategy
        tweets_per_account = min(50, max(5, available_quota // len(prioritized_accounts)))
        
        plan = {
            'available_quota': available_quota,
            'accounts_to_fetch': prioritized_accounts[:min(len(prioritized_accounts), available_quota // 10)],
            'tweets_per_account': tweets_per_account,
            'estimated_usage': len(prioritized_accounts) * tweets_per_account,
            'fetch_delay': self._calculate_optimal_delay(available_quota)
        }
        
        self.logger.info(f"🎯 Fetch Plan: {len(plan['accounts_to_fetch'])} accounts, {tweets_per_account} tweets each")
        return plan
    
    def _get_monthly_limit(self) -> int:
        """Get monthly tweet limit based on API tier"""
        # Try to detect API tier or use conservative estimate
        return 1500  # Free tier default - user should update this
    
    def _prioritize_accounts(self, accounts: List[str], state: Dict) -> List[str]:
        """Prioritize accounts based on competitive intelligence value"""
        
        # Tier 1: Direct competitors (highest priority)
        tier1 = ["aircall", "RingCentral", "dialpad", "8x8", "twilio"]
        
        # Tier 2: Conversation intelligence competitors  
        tier2 = ["GongInc", "ChorusAI", "fireflies_ai", "people_ai"]
        
        # Tier 3: Adjacent competitors
        tier3 = ["zoom", "MicrosoftTeams", "SlackHQ", "salesflare", "crayon_co"]
        
        # Tier 4: Others
        tier4 = [acc for acc in accounts if acc not in tier1 + tier2 + tier3]
        
        # Shuffle within tiers based on recent success/failure rates
        prioritized = []
        for tier in [tier1, tier2, tier3, tier4]:
            tier_accounts = [acc for acc in accounts if acc in tier]
            # Sort by success rate (accounts that worked recently get priority)
            tier_accounts.sort(key=lambda acc: state.get('account_priority', {}).get(acc, 0.5), reverse=True)
            prioritized.extend(tier_accounts)
        
        return prioritized
    
    def _calculate_optimal_delay(self, available_quota: int) -> int:
        """Calculate optimal delay between requests"""
        if available_quota > 1000:
            return 5  # Aggressive
        elif available_quota > 500:
            return 10  # Moderate
        elif available_quota > 100:
            return 20  # Conservative
        else:
            return 30  # Very conservative
    
    async def fetch_with_quota_management(self, username: str, since: datetime, max_tweets: int = 50) -> List:
        """Fetch tweets with intelligent quota management"""
        state = self.load_quota_state()
        
        try:
            # Use Twitter API v2 for better rate limit info
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                username=username,
                max_results=min(max_tweets, 100),
                start_time=since,
                tweet_fields=['created_at', 'text', 'public_metrics', 'context_annotations']
            ).flatten(limit=max_tweets)
            
            tweet_list = []
            for tweet in tweets:
                tweet_list.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'url': f"https://twitter.com/{username}/status/{tweet.id}",
                    'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else None
                })
            
            # Update quota state
            state['tweets_fetched'] = state.get('tweets_fetched', 0) + len(tweet_list)
            state['account_priority'][username] = state.get('account_priority', {}).get(username, 0.5) + 0.1
            
            self.save_quota_state(state)
            
            self.logger.info(f"✅ @{username}: {len(tweet_list)} tweets (Total quota used: {state['tweets_fetched']})")
            return tweet_list
            
        except Exception as e:
            # Update failure rate
            state['account_priority'][username] = state.get('account_priority', {}).get(username, 0.5) - 0.1
            self.save_quota_state(state)
            
            self.logger.error(f"❌ @{username}: {str(e)}")
            return []

class TwitterAlternatives:
    """Alternative approaches when Twitter API limits are hit"""
    
    @staticmethod
    def get_alternative_sources() -> List[Dict]:
        """Get alternative sources for competitor intelligence"""
        return [
            {
                "name": "Company Press Releases",
                "urls": [
                    "https://www.ringcentral.com/news/rss.xml",
                    "https://www.dialpad.com/press-releases/rss",
                    "https://www.8x8.com/news/rss"
                ],
                "type": "rss"
            },
            {
                "name": "LinkedIn Company Pages",
                "note": "Can be scraped with LinkedIn API or web scraping",
                "companies": ["aircall", "ringcentral", "dialpad", "gong-io"]
            },
            {
                "name": "Google Alerts",
                "note": "Set up Google Alerts for competitor names",
                "keywords": ["Aircall", "RingCentral", "Dialpad", "Gong", "conversation intelligence"]
            },
            {
                "name": "News API Services",
                "services": [
                    "NewsAPI.org (30k requests/month free)",
                    "Bing News API", 
                    "Google News API"
                ]
            }
        ]

def create_twitter_upgrade_plan():
    """Create plan for Twitter API upgrade"""
    print("🚀 Twitter API Upgrade Recommendations:")
    print()
    print("📊 Current Situation:")
    print("  - Free Tier: 1,500 tweets/month")
    print("  - Rate limited after ~3-5 accounts")
    print("  - Missing competitor intelligence")
    print()
    print("💡 Recommended Upgrade: Basic Tier ($100/month)")
    print("  - 10,000 tweets/month (6.7x increase)")
    print("  - Monitor 20-30 competitor accounts effectively")
    print("  - ~333 tweets per account per month")
    print("  - ROI: Competitive intelligence worth >> $100/month")
    print()
    print("📈 Alternative: Pro Tier ($5,000/month)")
    print("  - 1M tweets/month")
    print("  - Full competitor monitoring (50+ accounts)")
    print("  - Advanced analytics and insights")
    print()
    print("🔧 Immediate Actions:")
    print("  1. Go to https://developer.twitter.com/portal/dashboard")
    print("  2. Upgrade to Basic tier")
    print("  3. Update quota limits in TwitterQuotaManager")
    print("  4. Re-run competitive intelligence agent")

if __name__ == "__main__":
    create_twitter_upgrade_plan()