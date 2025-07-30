"""
Content processing and AI-powered summarization engine
"""

import asyncio
import openai
from typing import List, Dict, Optional
import json
import re
from datetime import datetime

from .sources import ContentItem

class ContentProcessor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.openai_client = None
        
        if config.openai_api_key and config.openai_api_key != "your_openai_api_key_here":
            try:
                self.openai_client = openai.OpenAI(api_key=config.openai_api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
                self.openai_client = None
    
    async def process_content(self, items: List[ContentItem]) -> List[ContentItem]:
        """Process all content items: categorize, score relevance, and summarize"""
        self.logger.info(f"Processing {len(items)} content items...")
        
        # Categorize items
        items = self._categorize_items(items)
        
        # Score relevance
        items = self._score_relevance(items)
        
        # Filter by relevance threshold
        items = [item for item in items if item.relevance_score >= self.config.relevance_threshold]
        
        # Deduplicate similar items
        items = self._deduplicate_items(items)
        
        # Generate summaries
        items = await self._generate_summaries(items)
        
        # Sort by relevance score
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        self.logger.info(f"Processed {len(items)} relevant items")
        return items
    
    def _categorize_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """Categorize items based on keywords"""
        for item in items:
            item.category = self._determine_category(item)
        return items
    
    def _determine_category(self, item: ContentItem) -> str:
        """Determine the category of a content item with enhanced keyword matching"""
        text = f"{item.title} {item.content}".lower()
        
        best_category = "General"
        best_score = 0
        
        for category in self.config.categories:
            score = 0
            for keyword in category.keywords:
                keyword_lower = keyword.lower()
                
                # Enhanced matching: exact match, word boundaries, and fuzzy variants
                if self._enhanced_keyword_match(keyword_lower, text):
                    # Title matches get higher weight
                    if keyword_lower in item.title.lower():
                        score += 2.0
                    else:
                        score += 1.0
            
            # Weight by priority (lower priority number = higher importance)
            weighted_score = score / category.priority
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_category = category.name
        
        return best_category
    
    def _enhanced_keyword_match(self, keyword: str, text: str) -> bool:
        """Enhanced keyword matching with word boundaries and variations"""
        import re
        
        # Direct substring match (existing behavior)
        if keyword in text:
            return True
        
        # Word boundary matching for better accuracy
        if len(keyword) <= 3:  # Short keywords need word boundaries
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                return True
        
        # Handle company name variations
        company_variations = {
            'ringcentral': ['ring central', 'ring-central'],
            'microsoft teams': ['ms teams', 'teams'],
            'five9': ['five 9', 'five-9'],
            '8x8': ['8 x 8', 'eight by eight'],
            'gong.io': ['gong io', 'gong'],
            'openai': ['open ai', 'open-ai'],
            'y combinator': ['ycombinator', 'yc']
        }
        
        if keyword in company_variations:
            for variant in company_variations[keyword]:
                if variant in text:
                    return True
        
        return False

    def _score_relevance(self, items: List[ContentItem]) -> List[ContentItem]:
        """Score items based on relevance to Aircall's interests"""
        for item in items:
            item.relevance_score = self._calculate_relevance_score(item)
        return items
    
    def _calculate_relevance_score(self, item: ContentItem) -> float:
        """Calculate relevance score focused specifically on Aircall's business domain"""
        text = f"{item.title} {item.content}".lower()
        score = 0.0
        
        # EXCLUSION FILTERS - Return 0.0 for irrelevant content (reduced for debugging)
        exclusion_keywords = [
            # Only hard exclusions for clearly unrelated content
            "kindle", "ipad", "iphone", "watch", "airpods", "headphones", "smartphone", "tablet", "laptop", 
            "ev truck", "electric vehicle", "car", "tesla", "drone", "robot", "pool cleaner", "luggage", "camera",
            "protein design", "biology", "biotech", "pharmaceutical", "drug", "medical device", "healthcare device",
            "font", "typography", "css", "daisyui", "tailwind"
        ]
        
        # Skip items with exclusion keywords unless they also have strong business relevance
        has_exclusion = any(keyword in text for keyword in exclusion_keywords)
        
        # CRITICAL - Direct Aircall business relevance (must have one of these)
        critical_keywords = [
            # Direct competitors
            "aircall", "ringcentral", "8x8", "dialpad", "vonage", "twilio", "five9", "genesys",
            # Voice/phone systems
            "cloud phone", "voip", "business phone", "phone system", "call center software",
            "contact center", "cloud calling", "voice api", "telephony",
            # Conversation intelligence (direct competition)
            "conversation intelligence", "call analytics", "call recording", "call coaching",
            "sales calls", "call transcription", "voice analytics"
        ]
        
        # HIGH - Adjacent technologies that could impact Aircall
        high_value_keywords = [
            # UCaaS/Communications
            "ucaas", "unified communications", "business communication", "team communication",
            "webrtc", "sip", "communication platform",
            # Sales/Support specific to voice
            "inside sales", "outbound sales", "sales calls", "phone sales", "telemarketing",
            "customer support calls", "support automation", "agent assistance",
            # Voice AI (specific to calls/phone)
            "voice ai", "speech recognition", "call automation", "voice bot",
            "conversational ai" # only if in phone/call context
        ]
        
        # MEDIUM - Related but broader technologies
        medium_value_keywords = [
            # CRM/Sales (only if phone/call related)
            "crm integration", "sales automation", "revenue operations",
            # General communication tech
            "messaging platform", "collaboration tools", "remote work communication"
        ]
        
        # More inclusive relevance check - allow multiple pathways to relevance
        has_critical = any(self._enhanced_keyword_match(keyword, text) for keyword in critical_keywords)
        has_phone_context = any(phone_word in text for phone_word in ["phone system", "voip", "telephony", "call center", "contact center", "voice api"])
        has_high_value = any(self._enhanced_keyword_match(keyword, text) for keyword in high_value_keywords)
        
        # Multiple ways an item can be relevant:
        # 1. Has critical business keywords
        # 2. Has high-value keywords (broader tech/business terms)
        # 3. Has phone context + any business relevance
        # 4. Contains competitor names or relevant business terms
        
        competitor_names = ["gong", "chorus", "dialpad", "ringcentral", "8x8", "twilio", "zoom", "microsoft teams", "slack"]
        has_competitor = any(comp in text for comp in competitor_names)
        
        business_terms = ["saas", "software", "startup", "funding", "ai", "automation", "crm", "sales", "customer"]
        has_business = any(term in text for term in business_terms)
        
        # Apply exclusion filter - if item has exclusions and no critical business relevance, exclude it
        if has_exclusion and not has_critical:
            return 0.0  # Excluded: hardware/generic AI/political content without business relevance
        
        # ADDITIONAL: Hard exclusion for financial titles regardless of business relevance
        title_text = item.title.lower()
        financial_title_keywords = [
            # Financial/Investment content
            "announce financial results", "financial results", "quarterly results", "earnings report", "earnings call", "earnings",
            "second quarter", "third quarter", "fourth quarter", "first quarter", "q1", "q2", "q3", "q4",
            "announce second quarter", "announce third quarter", "announce fourth quarter", "announce first quarter",
            "post q1 earnings", "post q2 earnings", "post q3 earnings", "post q4 earnings", "upcoming earnings",
            "analyst questions", "financial performance", "investment outlook", "long-term investment",
            "financial management", "financial outcomes", "good long term investment", "exceptional financial",
            "debt management", "financial measures", "prudent use of debt", "responsible financial",
            
            # Investment/Stock analysis sources and content
            "stock titan", "gurufocus", "marketbeat", "stock news", "investment case", "yahoo finance", "seeking alpha", 
            "ainvest", "investing.com", "zacks investment research", "tipranks", "streetinsider", "simplywall.st",
            "autocar professional", "printweek", "tradingview", "business wire", "msn",
            
            # Stock trading/investment language
            "buy, sell, or hold", "rating upgrade", "rating downgrade", "moody's upgrades", "consensus rating",
            "price target", "analyst rating", "strong growth stock", "strong value stock", "strong momentum stock",
            "top momentum stock", "top growth stock", "trending stock", "market outperform", "moderate buy",
            "stock soars", "stock sinks", "shares up", "shares down", "stock price", "stock is trading",
            "stock deserves your investment", "bullish analyst ratings", "analyst expect", "wall street analysts",
            "market performance", "exceptional market performance", "stock rating reiterated", "given consensus rating",
            
            # Investment fund activity
            "capital management", "retirement fund", "asset management", "sells shares", "buys shares", "purchases shares",
            "grows position", "reduces position", "sells position", "strategic advisors", "investment advisors",
            
            # Stock ticker references in titles
            "(rng)", "(twlo)", "(fivn)", "nyse:twlo", "nasdaq:fivn",
            
            # Investment advice/analysis
            "should you invest", "time to buy", "further upside", "easy gains", "rally 25", "potential to rally",
            "what drives", "stock price", "jim cramer", "wish i could be more positive"
        ]
        
        if any(keyword in title_text for keyword in financial_title_keywords):
            return 0.0  # Hard exclusion for financial news titles
        
        if not (has_critical or has_high_value or (has_phone_context and has_business) or has_competitor):
            return 0.0  # Not relevant to Aircall's business
        
        # Score based on keyword presence
        for keyword in critical_keywords:
            if self._enhanced_keyword_match(keyword, text):
                # Higher score for title mentions
                if self._enhanced_keyword_match(keyword, item.title.lower()):
                    score += 0.7
                else:
                    score += 0.5
        
        for keyword in high_value_keywords:
            if self._enhanced_keyword_match(keyword, text):
                if self._enhanced_keyword_match(keyword, item.title.lower()):
                    score += 0.4
                else:
                    score += 0.3
        
        for keyword in medium_value_keywords:
            if self._enhanced_keyword_match(keyword, text):
                score += 0.1
        
        # Boost for direct competitor mentions
        direct_competitors = ["ringcentral", "8x8", "dialpad", "twilio", "five9", "genesys"]
        for competitor in direct_competitors:
            if self._enhanced_keyword_match(competitor, text):
                # Extra boost for competitor names in title
                if self._enhanced_keyword_match(competitor, item.title.lower()):
                    score += 0.6
                else:
                    score += 0.4
        
        # Lower priority competitors (less relevant to Aircall's core business)
        secondary_competitors = ["vonage"]
        for competitor in secondary_competitors:
            if self._enhanced_keyword_match(competitor, text):
                # Reduced boost for secondary competitors
                if self._enhanced_keyword_match(competitor, item.title.lower()):
                    score += 0.2
                else:
                    score += 0.1
        
        # Boost score for recent items
        try:
            if hasattr(item, 'published') and item.published:
                if item.published.tzinfo is None:
                    published_naive = item.published
                else:
                    published_naive = item.published.replace(tzinfo=None)
                hours_old = (datetime.now() - published_naive).total_seconds() / 3600
            else:
                hours_old = 24  # Default if no published date
        except (AttributeError, TypeError, ValueError):
            hours_old = 24  # Default to 24 hours if we can't calculate
        if hours_old < 24:
            score += 0.1
        elif hours_old < 48:
            score += 0.05
        
        # Boost for competitor Twitter accounts
        if "twitter" in item.source.lower():
            competitor_accounts = ["aircall", "ringcentral", "8x8", "dialpad", "twilio", "zoom", "five9", "genesys"]
            source_lower = item.source.lower()
            if any(comp in source_lower for comp in competitor_accounts):
                score += 0.5  # Major boost for competitor social media
        
        # Category-based scoring (refined for Aircall focus)
        category_scores = {
            "Competitor Intelligence": 0.5,
            "Conversation Intelligence & Real-Time Assistance": 0.4,
            "AI Voice Technology": 0.3,
            "UCaaS & Cloud Communications": 0.3,
            "Contact Center & Customer Support": 0.2,
            "Sales & CRM Technology": 0.1,  # Reduced unless call-specific
            "Regulatory & Compliance": 0.2,
            "Industry Analysis & Reports": 0.1
        }
        
        score += category_scores.get(item.category, 0.0)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _deduplicate_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """Remove duplicate and very similar items"""
        if not items:
            return items
            
        deduplicated = []
        seen_titles = set()
        
        for item in items:
            # Normalize title for comparison
            normalized_title = self._normalize_title_for_dedup(item.title)
            
            # Skip if we've seen this exact normalized title
            if normalized_title in seen_titles:
                continue
            
            # Check for very similar titles
            is_duplicate = False
            for existing_title in seen_titles:
                if self._titles_are_similar(normalized_title, existing_title):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(normalized_title)
                deduplicated.append(item)
        
        self.logger.info(f"Deduplicated: {len(items)} -> {len(deduplicated)} items")
        return deduplicated
    
    def _normalize_title_for_dedup(self, title: str) -> str:
        """Normalize title for deduplication by removing source names and common variations"""
        normalized = title.lower().strip()
        
        # Remove source names that often appear in titles
        sources_to_remove = [
            "- yahoo finance", "- marketbeat", "- seeking alpha", "- investing.com", 
            "- tipranks", "- zacks investment research", "- streetinsider", "- business wire",
            "- cmswire.com", "- citybiz", "- simplywall.st", "- autocar professional",
            "- printweek.in", "- tradingview", "- msn", "- ainvest", "| rng stock news",
            "- gurufocus", "- stock titan"
        ]
        
        for source in sources_to_remove:
            if normalized.endswith(source):
                normalized = normalized[:-len(source)].strip()
        
        # Remove stock ticker references
        import re
        normalized = re.sub(r'\s*\([a-z]+:[a-z]+\)\s*', ' ', normalized)
        normalized = re.sub(r'\s*\([a-z]+\)\s*', ' ', normalized)
        
        # Clean up extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _titles_are_similar(self, title1: str, title2: str) -> bool:
        """Check if two normalized titles are very similar (likely duplicates)"""
        # If titles are identical after normalization
        if title1 == title2:
            return True
        
        # Check for high similarity using simple word overlap
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        # Skip very short titles
        if len(words1) < 3 or len(words2) < 3:
            return False
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return False
        
        similarity = intersection / union
        
        # Consider similar if 80% word overlap
        return similarity >= 0.8
    
    async def _generate_summaries(self, items: List[ContentItem]) -> List[ContentItem]:
        """Generate AI-powered summaries for items"""
        if not self.openai_client:
            self.logger.warning("OpenAI client not available, skipping summary generation")
            return items
        
        # Process items in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            await self._process_batch_summaries(batch)
            await asyncio.sleep(1)  # Rate limiting
        
        return items
    
    async def _process_batch_summaries(self, items: List[ContentItem]):
        """Process a batch of items for summary generation"""
        tasks = []
        for item in items:
            if len(item.content) > 100:  # Only summarize substantial content
                task = asyncio.create_task(self._generate_summary(item))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _generate_summary(self, item: ContentItem):
        """Generate AI summary for a single item"""
        try:
            prompt = f"""
            Create an objective summary of the following content for a competitive intelligence digest.
            
            Requirements:
            1. Identify the PRIMARY COMPANY mentioned in the title/content first
            2. Create an objective summary of what happened - keep it factual without implications or recommendations
            3. Focus on: product launches, acquisitions, funding, partnerships, feature updates, market developments, regulatory changes
            4. Format as two separate parts:
               - "COMPANY: [Company Name] - [one-line description of what they do]"
               - "SUMMARY: [Objective summary of what happened]"
            5. Keep total length under {self.config.summary_max_length} characters
            6. Use neutral, factual tone without speculation
            
            Example format:
            "COMPANY: Five9 - Cloud-based contact center software provider.
            SUMMARY: Five9 released a new CX report highlighting AI adoption challenges in contact centers, showing that 60% of organizations struggle with implementation costs."
            
            Title: {item.title}
            Content: {item.content[:1000]}
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            item.summary = summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary for item {item.title}: {str(e)}")
            item.summary = item.content[:self.config.summary_max_length] + "..."

class DigestGenerator:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def generate_digest(self, items: List[ContentItem]) -> Dict:
        """Generate structured digest from processed items"""
        # Group items by category
        categorized_items = {}
        for item in items:
            category = item.category
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append(item)
        
        # Sort categories by priority
        category_order = {cat.name: cat.priority for cat in self.config.categories}
        sorted_categories = sorted(categorized_items.keys(), 
                                 key=lambda x: category_order.get(x, 999))
        
        # Create digest structure
        # Check for trend insights from first item
        trend_insights = None
        if items and hasattr(items[0], "trend_insights"):
            trend_insights = items[0].trend_insights
        
        # Create digest structure
        digest = {
            "generated_at": datetime.now().isoformat(),
            "total_items": len(items),
            "categories": {},
            "summary_stats": self._generate_summary_stats(items),
            "trend_insights": trend_insights
        }        
        for category in sorted_categories:
            category_items = categorized_items[category]
            
            # Sort items within category by relevance
            category_items.sort(key=lambda x: x.relevance_score, reverse=True)
            
            digest["categories"][category] = {
                "count": len(category_items),
                "items": [item.to_dict() for item in category_items]
            }
        
        return digest
    
    def _generate_summary_stats(self, items: List[ContentItem]) -> Dict:
        """Generate summary statistics for the digest"""
        if not items:
            return {"total": 0, "sources": {}, "date_range": None, "avg_relevance": 0.0}
        
        sources = {}
        for item in items:
            sources[item.source] = sources.get(item.source, 0) + 1
        
        dates = []
        for item in items:
            if hasattr(item, 'published') and item.published:
                try:
                    if item.published.tzinfo is None:
                        dates.append(item.published)
                    else:
                        dates.append(item.published.replace(tzinfo=None))
                except (AttributeError, TypeError):
                    continue
        
        if dates:
            date_range = {
                "from": min(dates).isoformat(),
                "to": max(dates).isoformat()
            }
        else:
            date_range = None
        
        return {
            "total": len(items),
            "sources": sources,
            "date_range": date_range,
            "avg_relevance": sum(item.relevance_score for item in items) / len(items)
        }