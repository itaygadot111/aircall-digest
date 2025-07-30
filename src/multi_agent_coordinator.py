"""
Multi-Agent Workflow Coordinator for Competitive Intelligence
Orchestrates specialized agents for different analysis types
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json

from .sources import ContentItem
from .langchain_processor import LangChainProcessor

class AgentType(Enum):
    PRODUCT_INTELLIGENCE = "product_intelligence"
    MARKET_ANALYSIS = "market_analysis"  
    TECHNOLOGY_TRENDS = "technology_trends"
    COMPETITIVE_MOVES = "competitive_moves"
    REGULATORY_COMPLIANCE = "regulatory_compliance"

class SpecializedAgent:
    """Base class for specialized competitive intelligence agents"""
    
    def __init__(self, agent_type: AgentType, config, logger):
        self.agent_type = agent_type
        self.config = config
        self.logger = logger
        self.processor = LangChainProcessor(config, logger)
    
    async def analyze(self, items: List[ContentItem]) -> Dict:
        """Override in specialized agents"""
        raise NotImplementedError
    
    def filter_relevant_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """Filter items relevant to this agent's specialty"""
        return [item for item in items if self.is_relevant(item)]
    
    def is_relevant(self, item: ContentItem) -> bool:
        """Override in specialized agents to define relevance criteria"""
        return True

class ProductIntelligenceAgent(SpecializedAgent):
    """Analyzes competitor product launches, features, and roadmap intelligence"""
    
    def __init__(self, config, logger):
        super().__init__(AgentType.PRODUCT_INTELLIGENCE, config, logger)
        self.focus_keywords = [
            "product launch", "new feature", "beta", "roadmap", "integration",
            "api", "platform", "dashboard", "mobile app", "chrome extension",
            "workflow automation", "analytics", "reporting", "customization"
        ]
    
    def is_relevant(self, item: ContentItem) -> bool:
        text = f"{item.title} {item.content}".lower()
        return (
            any(keyword in text for keyword in self.focus_keywords) or
            item.category in ["Feature & Product Updates", "Competitor Intelligence"] or
            "product" in text or "feature" in text
        )
    
    async def analyze(self, items: List[ContentItem]) -> Dict:
        """Analyze product intelligence from content items"""
        relevant_items = self.filter_relevant_items(items)
        
        if len(relevant_items) < 2:
            return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            prompt = ChatPromptTemplate.from_template("""
            You are a product intelligence analyst for Aircall (cloud phone system).
            
            Analyze the following content for product-related competitive intelligence:
            
            {content}
            
            Provide analysis in this format:
            PRODUCT_LAUNCHES:
            - [New product/feature launch 1]
            - [New product/feature launch 2]
            
            FEATURE_GAPS:
            - [Potential gap in Aircall's offering]
            - [Competitive advantage opportunity]
            
            INTEGRATION_TRENDS:
            - [Popular integration/platform trend]
            - [API/platform development trend]
            
            ROADMAP_INTEL:
            - [Competitor roadmap insight]
            - [Technology direction insight]
            """)
            
            content_summary = "\n\n".join([
                f"Title: {item.title}\nSource: {item.source}\nContent: {item.content[:300]}..."
                for item in relevant_items[:3]
            ])
            
            if self.processor.chat_model:
                chain = prompt | self.processor.chat_model | StrOutputParser()
                analysis = await asyncio.to_thread(
                    chain.invoke, {"content": content_summary}
                )
                
                insights = self._parse_product_analysis(analysis)
                return {
                    "agent_type": self.agent_type.value,
                    "insights": insights,
                    "items_analyzed": len(relevant_items),
                    "top_items": [item.to_dict() for item in relevant_items[:2]]
                }
        
        except Exception as e:
            self.logger.error(f"Product intelligence analysis failed: {str(e)}")
        
        return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
    
    def _parse_product_analysis(self, analysis: str) -> Dict:
        """Parse structured product analysis"""
        result = {
            "product_launches": [],
            "feature_gaps": [],
            "integration_trends": [],
            "roadmap_intel": []
        }
        
        current_section = None
        lines = analysis.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('PRODUCT_LAUNCHES:'):
                current_section = "product_launches"
            elif line.startswith('FEATURE_GAPS:'):
                current_section = "feature_gaps"  
            elif line.startswith('INTEGRATION_TRENDS:'):
                current_section = "integration_trends"
            elif line.startswith('ROADMAP_INTEL:'):
                current_section = "roadmap_intel"
            elif line.startswith('- ') and current_section:
                clean_line = line[2:].strip()
                if clean_line:
                    result[current_section].append(clean_line)
        
        return result

class MarketAnalysisAgent(SpecializedAgent):
    """Analyzes market trends, funding, acquisitions, and competitive positioning"""
    
    def __init__(self, config, logger):
        super().__init__(AgentType.MARKET_ANALYSIS, config, logger)
        self.focus_keywords = [
            "funding", "acquisition", "merger", "ipo", "valuation", "market share",
            "revenue", "growth", "expansion", "partnership", "investment",
            "series a", "series b", "series c", "venture", "round"
        ]
    
    def is_relevant(self, item: ContentItem) -> bool:
        text = f"{item.title} {item.content}".lower()
        return (
            any(keyword in text for keyword in self.focus_keywords) or
            "market" in text or "business" in text or "$" in text
        )
    
    async def analyze(self, items: List[ContentItem]) -> Dict:
        """Analyze market and business intelligence"""
        relevant_items = self.filter_relevant_items(items)
        
        if len(relevant_items) < 2:
            return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            prompt = ChatPromptTemplate.from_template("""
            You are a market intelligence analyst for Aircall (cloud phone system).
            
            Analyze the following content for market and business intelligence:
            
            {content}
            
            Provide analysis in this format:
            FUNDING_ACTIVITY:
            - [Funding round or investment news]
            - [M&A activity in the space]
            
            MARKET_MOVEMENTS:
            - [Market shift or trend]
            - [Competitive positioning change]
            
            BUSINESS_STRATEGY:
            - [Strategic business move]
            - [Partnership or expansion]
            
            THREATS_OPPORTUNITIES:
            - [Market threat to Aircall]
            - [Market opportunity for Aircall]
            """)
            
            content_summary = "\n\n".join([
                f"Title: {item.title}\nSource: {item.source}\nContent: {item.content[:300]}..."
                for item in relevant_items[:3]
            ])
            
            if self.processor.chat_model:
                chain = prompt | self.processor.chat_model | StrOutputParser()
                analysis = await asyncio.to_thread(
                    chain.invoke, {"content": content_summary}
                )
                
                insights = self._parse_market_analysis(analysis)
                return {
                    "agent_type": self.agent_type.value,
                    "insights": insights,
                    "items_analyzed": len(relevant_items),
                    "top_items": [item.to_dict() for item in relevant_items[:2]]
                }
        
        except Exception as e:
            self.logger.error(f"Market analysis failed: {str(e)}")
        
        return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
    
    def _parse_market_analysis(self, analysis: str) -> Dict:
        """Parse structured market analysis"""
        result = {
            "funding_activity": [],
            "market_movements": [],
            "business_strategy": [],
            "threats_opportunities": []
        }
        
        current_section = None
        lines = analysis.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('FUNDING_ACTIVITY:'):
                current_section = "funding_activity"
            elif line.startswith('MARKET_MOVEMENTS:'):
                current_section = "market_movements"
            elif line.startswith('BUSINESS_STRATEGY:'):
                current_section = "business_strategy"
            elif line.startswith('THREATS_OPPORTUNITIES:'):
                current_section = "threats_opportunities"
            elif line.startswith('- ') and current_section:
                clean_line = line[2:].strip()
                if clean_line:
                    result[current_section].append(clean_line)
        
        return result

class TechnologyTrendsAgent(SpecializedAgent):
    """Analyzes emerging technologies, AI developments, and technical innovations"""
    
    def __init__(self, config, logger):
        super().__init__(AgentType.TECHNOLOGY_TRENDS, config, logger)
        self.focus_keywords = [
            "artificial intelligence", "machine learning", "ai", "automation",
            "cloud", "api", "integration", "security", "privacy", "gdpr",
            "webrtc", "sip", "voip", "real-time", "latency", "infrastructure"
        ]
    
    def is_relevant(self, item: ContentItem) -> bool:
        text = f"{item.title} {item.content}".lower()
        return (
            any(keyword in text for keyword in self.focus_keywords) or
            item.category in ["AI Voice Technology", "UCaaS & Cloud Communications"] or
            "technology" in text or "innovation" in text
        )
    
    async def analyze(self, items: List[ContentItem]) -> Dict:
        """Analyze technology trends and innovations"""
        relevant_items = self.filter_relevant_items(items)
        
        if len(relevant_items) < 2:
            return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            prompt = ChatPromptTemplate.from_template("""
            You are a technology intelligence analyst for Aircall (cloud phone system).
            
            Analyze the following content for technology trends and innovations:
            
            {content}
            
            Provide analysis in this format:
            EMERGING_TECH:
            - [Emerging technology trend]
            - [Innovation in communications/AI]
            
            AI_DEVELOPMENTS:
            - [AI advancement relevant to voice/communications]
            - [Machine learning application]
            
            INFRASTRUCTURE_TRENDS:
            - [Cloud/API/platform trend]
            - [Security/compliance development]
            
            TECH_THREATS:
            - [Technology that could disrupt current model]
            - [Technical challenge or limitation emerging]
            """)
            
            content_summary = "\n\n".join([
                f"Title: {item.title}\nSource: {item.source}\nContent: {item.content[:300]}..."
                for item in relevant_items[:3]
            ])
            
            if self.processor.chat_model:
                chain = prompt | self.processor.chat_model | StrOutputParser()
                analysis = await asyncio.to_thread(
                    chain.invoke, {"content": content_summary}
                )
                
                insights = self._parse_tech_analysis(analysis)
                return {
                    "agent_type": self.agent_type.value,
                    "insights": insights,
                    "items_analyzed": len(relevant_items),
                    "top_items": [item.to_dict() for item in relevant_items[:2]]
                }
        
        except Exception as e:
            self.logger.error(f"Technology trends analysis failed: {str(e)}")
        
        return {"agent_type": self.agent_type.value, "insights": [], "items_analyzed": len(relevant_items)}
    
    def _parse_tech_analysis(self, analysis: str) -> Dict:
        """Parse structured technology analysis"""
        result = {
            "emerging_tech": [],
            "ai_developments": [],
            "infrastructure_trends": [],
            "tech_threats": []
        }
        
        current_section = None
        lines = analysis.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('EMERGING_TECH:'):
                current_section = "emerging_tech"
            elif line.startswith('AI_DEVELOPMENTS:'):
                current_section = "ai_developments"
            elif line.startswith('INFRASTRUCTURE_TRENDS:'):
                current_section = "infrastructure_trends"
            elif line.startswith('TECH_THREATS:'):
                current_section = "tech_threats"
            elif line.startswith('- ') and current_section:
                clean_line = line[2:].strip()
                if clean_line:
                    result[current_section].append(clean_line)
        
        return result

class MultiAgentCoordinator:
    """Coordinates multiple specialized agents for comprehensive analysis"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Initialize specialized agents
        self.agents = {
            AgentType.PRODUCT_INTELLIGENCE: ProductIntelligenceAgent(config, logger),
            AgentType.MARKET_ANALYSIS: MarketAnalysisAgent(config, logger),
            AgentType.TECHNOLOGY_TRENDS: TechnologyTrendsAgent(config, logger)
        }
    
    async def coordinate_analysis(self, items: List[ContentItem]) -> Dict:
        """Coordinate analysis across all specialized agents"""
        self.logger.info(f"Starting multi-agent analysis with {len(items)} items...")
        
        # Run all agents concurrently
        tasks = []
        for agent_type, agent in self.agents.items():
            task = asyncio.create_task(agent.analyze(items))
            tasks.append((agent_type, task))
        
        # Collect results
        agent_results = {}
        for agent_type, task in tasks:
            try:
                result = await task
                agent_results[agent_type.value] = result
                self.logger.info(f"{agent_type.value} analyzed {result['items_analyzed']} items")
            except Exception as e:
                self.logger.error(f"Agent {agent_type.value} failed: {str(e)}")
                agent_results[agent_type.value] = {"error": str(e), "items_analyzed": 0}
        
        # Synthesize cross-agent insights
        synthesis = await self._synthesize_insights(agent_results, items)
        
        return {
            "multi_agent_analysis": {
                "generated_at": datetime.now().isoformat(),
                "total_items_processed": len(items),
                "agent_results": agent_results,
                "cross_agent_synthesis": synthesis
            }
        }
    
    async def _synthesize_insights(self, agent_results: Dict, items: List[ContentItem]) -> Dict:
        """Synthesize insights across agents to identify cross-cutting themes"""
        try:
            # Collect all insights from agents
            all_insights = []
            for agent_type, result in agent_results.items():
                if "insights" in result:
                    for category, insights_list in result["insights"].items():
                        all_insights.extend(insights_list)
            
            if len(all_insights) < 3:
                return {"synthesis_available": False, "reason": "Insufficient insights for synthesis"}
            
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            # Check if we have access to LangChain models
            sample_agent = list(self.agents.values())[0]
            if not sample_agent.processor.chat_model:
                return {"synthesis_available": False, "reason": "No AI model available for synthesis"}
            
            prompt = ChatPromptTemplate.from_template("""
            You are synthesizing competitive intelligence insights for Aircall from multiple specialized analysts.
            
            Agent Insights:
            {insights}
            
            Provide synthesis in this format:
            STRATEGIC_PRIORITIES:
            - [Top strategic priority for Aircall]
            - [Second strategic priority]
            
            CROSS_CUTTING_THEMES:
            - [Theme that appears across product/market/tech analysis]
            - [Another cross-cutting theme]
            
            IMMEDIATE_ACTIONS:
            - [Urgent action item based on multiple insights]
            - [Another immediate action]
            
            LONG_TERM_IMPLICATIONS:
            - [Long-term strategic implication]
            - [Future competitive landscape prediction]
            """)
            
            insights_text = "\n".join([f"- {insight}" for insight in all_insights[:10]])
            
            chain = prompt | sample_agent.processor.chat_model | StrOutputParser()
            synthesis = await asyncio.to_thread(
                chain.invoke, {"insights": insights_text}
            )
            
            return {
                "synthesis_available": True,
                "strategic_priorities": self._extract_section(synthesis, "STRATEGIC_PRIORITIES:"),
                "cross_cutting_themes": self._extract_section(synthesis, "CROSS_CUTTING_THEMES:"),
                "immediate_actions": self._extract_section(synthesis, "IMMEDIATE_ACTIONS:"),
                "long_term_implications": self._extract_section(synthesis, "LONG_TERM_IMPLICATIONS:")
            }
            
        except Exception as e:
            self.logger.error(f"Cross-agent synthesis failed: {str(e)}")
            return {"synthesis_available": False, "error": str(e)}
    
    def _extract_section(self, text: str, section_header: str) -> List[str]:
        """Extract list items from a section of structured text"""
        lines = text.split('\n')
        section_items = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            if line.startswith(section_header):
                in_section = True
                continue
            elif line.startswith(('STRATEGIC_', 'CROSS_', 'IMMEDIATE_', 'LONG_')) and in_section:
                break
            elif in_section and line.startswith('- '):
                clean_line = line[2:].strip()
                if clean_line:
                    section_items.append(clean_line)
        
        return section_items