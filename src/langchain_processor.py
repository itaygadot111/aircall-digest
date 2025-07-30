"""
LangChain-powered content processor with semantic understanding and trend analysis
"""

import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .sources import ContentItem
from .processor import ContentProcessor


class LangChainProcessor(ContentProcessor):
    """Enhanced processor using LangChain for semantic understanding"""
    
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.embeddings = None
        self.chat_model = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize LangChain components if OpenAI key available
        if config.openai_api_key and config.openai_api_key != "your_openai_api_key_here":
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=config.openai_api_key,
                    model="text-embedding-3-small"
                )
                self.chat_model = ChatOpenAI(
                    openai_api_key=config.openai_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.3
                )
                self.logger.info("LangChain components initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LangChain components: {str(e)}")
                self.embeddings = None
                self.chat_model = None
    
    async def process_content(self, items: List[ContentItem]) -> List[ContentItem]:
        """Enhanced processing with semantic analysis"""
        self.logger.info(f"Processing {len(items)} items with LangChain enhancement...")
        
        # Standard processing first
        items = await super().process_content(items)
        
        if not items:
            return items
        
        # Enhanced LangChain processing
        if self.embeddings and self.chat_model:
            try:
                # Semantic categorization
                items = await self._semantic_categorization(items)
                
                # Competitive intelligence analysis
                items = await self._competitive_intelligence_analysis(items)
                
                # Trend analysis
                trend_insights = await self._trend_analysis(items)
                
                # Add trend insights to the first item for inclusion in digest
                if items and trend_insights:
                    items[0].trend_insights = trend_insights
                
                self.logger.info("LangChain enhancement completed successfully")
            except Exception as e:
                self.logger.error(f"LangChain processing failed: {str(e)}")
        
        return items
    
    async def _semantic_categorization(self, items: List[ContentItem]) -> List[ContentItem]:
        """Use embeddings for better categorization"""
        try:
            # Create category descriptions for embedding
            category_descriptions = {}
            for category in self.config.categories:
                # Create rich description from keywords
                keywords_text = ", ".join(category.keywords)
                category_descriptions[category.name] = f"{category.name}: {keywords_text}"
            
            # Get embeddings for categories
            category_texts = list(category_descriptions.values())
            category_embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents, category_texts
            )
            
            # Process items in batches to avoid rate limits
            batch_size = 5
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                # Get item embeddings
                item_texts = [f"{item.title} {item.content[:500]}" for item in batch]
                item_embeddings = await asyncio.to_thread(
                    self.embeddings.embed_documents, item_texts
                )
                
                # Calculate similarity and reassign categories
                for j, item in enumerate(batch):
                    similarities = cosine_similarity(
                        [item_embeddings[j]], category_embeddings
                    )[0]
                    
                    best_category_idx = np.argmax(similarities)
                    best_score = similarities[best_category_idx]
                    
                    # Only reassign if confidence is high enough
                    if best_score > 0.3:
                        category_names = list(category_descriptions.keys())
                        item.category = category_names[best_category_idx]
                        item.semantic_confidence = best_score
                
                # Rate limiting
                await asyncio.sleep(1)
            
            self.logger.info("Semantic categorization completed")
        except Exception as e:
            self.logger.error(f"Semantic categorization failed: {str(e)}")
        
        return items
    
    async def _competitive_intelligence_analysis(self, items: List[ContentItem]) -> List[ContentItem]:
        """Analyze competitive intelligence implications"""
        try:
            # Create analysis prompt
            analysis_prompt = ChatPromptTemplate.from_template("""
            You are a competitive intelligence analyst for Aircall, a cloud-based phone system company.
            
            Analyze the following content and provide:
            1. Competitive threat level (HIGH/MEDIUM/LOW)
            2. Key implications for Aircall
            3. Recommended actions (if any)
            4. Strategic category (Product, Market, Partnership, Funding, Technology)
            
            Content Title: {title}
            Content: {content}
            
            Provide your analysis in this format:
            THREAT_LEVEL: [HIGH/MEDIUM/LOW]
            IMPLICATIONS: [2-3 sentences]
            ACTIONS: [1-2 recommended actions or "None"]
            CATEGORY: [Product/Market/Partnership/Funding/Technology]
            """)
            
            chain = analysis_prompt | self.chat_model | StrOutputParser()
            
            # Analyze high-priority items
            competitor_items = [
                item for item in items 
                if item.category == "Competitor Intelligence" and item.relevance_score > 0.7
            ][:3]  # Limit to top 3 for cost control
            
            for item in competitor_items:
                try:
                    analysis = await asyncio.to_thread(
                        chain.invoke,
                        {
                            "title": item.title,
                            "content": item.content[:1000]
                        }
                    )
                    
                    # Parse analysis
                    item.competitive_analysis = self._parse_competitive_analysis(analysis)
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze item {item.title}: {str(e)}")
                
                await asyncio.sleep(1)  # Rate limiting
            
            self.logger.info(f"Competitive analysis completed for {len(competitor_items)} items")
        except Exception as e:
            self.logger.error(f"Competitive intelligence analysis failed: {str(e)}")
        
        return items
    
    def _parse_competitive_analysis(self, analysis: str) -> Dict:
        """Parse structured analysis from LLM response"""
        result = {
            "threat_level": "LOW",
            "implications": "",
            "actions": "None",
            "category": "Market"
        }
        
        try:
            lines = analysis.strip().split('\n')
            for line in lines:
                if line.startswith('THREAT_LEVEL:'):
                    result["threat_level"] = line.split(':', 1)[1].strip()
                elif line.startswith('IMPLICATIONS:'):
                    result["implications"] = line.split(':', 1)[1].strip()
                elif line.startswith('ACTIONS:'):
                    result["actions"] = line.split(':', 1)[1].strip()
                elif line.startswith('CATEGORY:'):
                    result["category"] = line.split(':', 1)[1].strip()
        except Exception as e:
            self.logger.warning(f"Failed to parse competitive analysis: {str(e)}")
        
        return result
    
    async def _trend_analysis(self, items: List[ContentItem]) -> Optional[Dict]:
        """Analyze trends across all content"""
        if len(items) < 3:
            return None
        
        try:
            # Prepare content for trend analysis
            recent_items = [
                item for item in items 
                if item.relevance_score > 0.5
            ][:5]
            
            content_summary = "\n\n".join([
                f"Title: {item.title}\nCategory: {item.category}\nContent: {item.content[:200]}..."
                for item in recent_items
            ])
            
            trend_prompt = ChatPromptTemplate.from_template("""
            You are analyzing competitive intelligence trends for Aircall (cloud phone system company).
            
            Based on the following recent content, identify:
            1. Top 2 emerging trends in the industry
            2. Key competitive movements
            3. Technology shifts that could impact Aircall
            
            Content:
            {content}
            
            Provide analysis in this format:
            TRENDS:
            1. [Trend 1]
            2. [Trend 2]
            
            COMPETITIVE_MOVES:
            - [Key competitive movement 1]
            - [Key competitive movement 2]
            
            TECH_SHIFTS:
            - [Technology shift 1]
            - [Technology shift 2]
            """)
            
            chain = trend_prompt | self.chat_model | StrOutputParser()
            
            analysis = await asyncio.to_thread(
                chain.invoke,
                {"content": content_summary}
            )
            
            return self._parse_trend_analysis(analysis)
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return None
    
    def _parse_trend_analysis(self, analysis: str) -> Dict:
        """Parse trend analysis from LLM response"""
        result = {
            "trends": [],
            "competitive_moves": [],
            "tech_shifts": []
        }
        
        try:
            current_section = None
            lines = analysis.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('TRENDS:'):
                    current_section = "trends"
                elif line.startswith('COMPETITIVE_MOVES:'):
                    current_section = "competitive_moves"
                elif line.startswith('TECH_SHIFTS:'):
                    current_section = "tech_shifts"
                elif line and current_section:
                    # Remove bullet points and numbers
                    clean_line = line.lstrip('- 1234567890. ')
                    if clean_line:
                        result[current_section].append(clean_line)
        
        except Exception as e:
            self.logger.warning(f"Failed to parse trend analysis: {str(e)}")
        
        return result