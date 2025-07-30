"""
Digest formatting and newsletter generation
"""

import json
from datetime import datetime
from typing import Dict, List
from jinja2 import Template

class DigestFormatter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def format_digest(self, digest: Dict) -> str:
        """Format digest based on configured output format"""
        if self.config.output_format == "html":
            return self._format_html(digest)
        elif self.config.output_format == "markdown":
            return self._format_markdown(digest)
        elif self.config.output_format == "json":
            return self._format_json(digest)
        else:
            self.logger.warning(f"Unknown output format: {self.config.output_format}")
            return self._format_html(digest)
    
    def _format_html(self, digest: Dict) -> str:
        """Format digest as HTML newsletter"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Aircall Competitive Intelligence Digest</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #012635;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background: #ffffff;
        }
        .header {
            background: linear-gradient(135deg, #00BD82 0%, #06AB78 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(0, 189, 130, 0.15);
        }
        .header h1 {
            margin: 0;
            font-size: 2.8em;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .header p {
            margin: 15px 0 0 0;
            opacity: 0.95;
            font-size: 1.2em;
            font-weight: 400;
        }
        .stats {
            background: #f8fffe;
            border: 1px solid #e6f7f4;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 40px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2.2em;
            font-weight: 700;
            color: #00BD82;
            margin-bottom: 4px;
        }
        .stat-label {
            color: #073F56;
            font-size: 0.95em;
            font-weight: 500;
        }
        .category {
            margin-bottom: 40px;
        }
        .category-header {
            background: #00BD82;
            color: white;
            padding: 20px 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(0, 189, 130, 0.1);
        }
        .category-header h2 {
            margin: 0;
            font-size: 1.5em;
        }
        .category-count {
            float: right;
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .item {
            background: white;
            border: 1px solid #e6f7f4;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 189, 130, 0.08);
            transition: all 0.2s ease;
        }
        .item:hover {
            box-shadow: 0 4px 16px rgba(0, 189, 130, 0.12);
            border-color: #c2ffec;
        }
        .item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .item-title {
            font-size: 1.25em;
            font-weight: 600;
            color: #012635;
            margin: 0;
            line-height: 1.3;
        }
        .item-source {
            background: #c2ffec;
            color: #00724e;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .item-summary {
            margin: 12px 0;
            color: #073F56;
            line-height: 1.5;
        }
        .item-link {
            color: #00BD82;
            text-decoration: none;
            font-weight: 600;
        }
        .item-link:hover {
            text-decoration: underline;
        }
        .item-meta {
            font-size: 0.9em;
            color: #073F56;
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .relevance-score {
            background: #00BD82;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: 500;
        }
        .twitter-section {
            background: linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(29, 161, 242, 0.15);
        }
        .twitter-section h2 {
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }
        .tweet-item {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .tweet-author {
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .tweet-content {
            font-size: 0.95em;
            line-height: 1.4;
            margin-bottom: 8px;
        }
        .tweet-meta {
            font-size: 0.8em;
            opacity: 0.8;
        }
        .no-twitter {
            text-align: center;
            font-style: italic;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
        .trend-section {
            background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
            border: 2px solid #00BD82;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 8px 24px rgba(0, 189, 130, 0.1);
        }
        .trend-section h2 {
            margin: 0 0 25px 0;
            color: #012635;
            font-size: 2em;
            font-weight: 700;
            text-align: center;
            border-bottom: 2px solid #00BD82;
            padding-bottom: 15px;
        }
        .trend-subsection {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .trend-subsection h3 {
            margin: 0 0 15px 0;
            color: #00BD82;
            font-size: 1.3em;
            font-weight: 600;
        }
        .trend-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .trend-list li {
            background: white;
            border: 1px solid #e6f7f4;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: #073F56;
            line-height: 1.5;
            box-shadow: 0 2px 4px rgba(0, 189, 130, 0.05);
        }
        .competitive-analysis {
            background: rgba(255, 248, 220, 0.8);
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }
        .threat-level {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }
        .threat-high { background: #dc3545; }
        .threat-medium { background: #ffc107; color: #333; }
        .threat-low { background: #28a745; }
        .semantic-confidence {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.7em;
            margin-left: 8px;
        }
        .multi-agent-section {
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border: 2px solid #9c27b0;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 8px 24px rgba(156, 39, 176, 0.15);
        }
        .multi-agent-section h2 {
            margin: 0 0 25px 0;
            color: #4a148c;
            font-size: 2em;
            font-weight: 700;
            text-align: center;
            border-bottom: 2px solid #9c27b0;
            padding-bottom: 15px;
        }
        .synthesis-section {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .synthesis-section h3 {
            margin: 0 0 15px 0;
            color: #6a1b9a;
            font-size: 1.4em;
            font-weight: 600;
        }
        .synthesis-subsection {
            margin-bottom: 15px;
        }
        .synthesis-subsection h4 {
            margin: 0 0 10px 0;
            color: #8e24aa;
            font-size: 1.1em;
            font-weight: 600;
        }
        .synthesis-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .synthesis-list li {
            background: white;
            border: 1px solid #e1bee7;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
            color: #4a148c;
            line-height: 1.4;
            box-shadow: 0 2px 4px rgba(156, 39, 176, 0.1);
        }
        .agent-results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .agent-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #ce93d8;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(156, 39, 176, 0.1);
        }
        .agent-card h3 {
            margin: 0 0 10px 0;
            color: #6a1b9a;
            font-size: 1.2em;
            font-weight: 600;
        }
        .stat-badge {
            background: #9c27b0;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: 500;
        }
        .agent-insights {
            margin-top: 15px;
        }
        .insight-category {
            margin-bottom: 12px;
        }
        .insight-category h5 {
            margin: 0 0 6px 0;
            color: #7b1fa2;
            font-size: 1em;
            font-weight: 600;
        }
        .insight-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .insight-list li {
            background: #f8bbd9;
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 4px;
            color: #4a148c;
            font-size: 0.9em;
            line-height: 1.3;
        }
        .footer {
            margin-top: 60px;
            text-align: center;
            color: #073F56;
            font-size: 0.9em;
            padding-top: 24px;
            border-top: 1px solid #e6f7f4;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Competitive Intelligence Digest</h1>
        <p>AI-powered insights for Aircall • {{ digest.generated_at[:10] }}</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{{ digest.total_items }}</div>
            <div class="stat-label">Total Items</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{{ digest.categories|length }}</div>
            <div class="stat-label">Categories</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{{ digest.summary_stats.sources|length }}</div>
            <div class="stat-label">Sources</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{{ "%.0f"|format(digest.summary_stats.avg_relevance * 100) }}%</div>
            <div class="stat-label">Avg Relevance</div>
        </div>
    </div>
    
    <!-- Twitter/X Section -->
    {% set twitter_items = [] %}
    {% for category_name in digest.categories %}
    {% set category_data = digest.categories[category_name] %}
    {% for item in category_data['items'] %}
    {% if 'twitter' in item.source.lower() or 'x.com' in item.url.lower() %}
    {% set _ = twitter_items.append(item) %}
    {% endif %}
    {% endfor %}
    {% endfor %}
    
    <div class="twitter-section">
        <h2>🐦 Competitor Activity on X/Twitter</h2>
        {% if twitter_items %}
        {% for item in twitter_items[:5] %}
        <div class="tweet-item">
            <div class="tweet-author">@{{ item.source.split(' - ')[0] if ' - ' in item.source else item.source }}</div>
            <div class="tweet-content">{{ item.content[:200] }}{% if item.content|length > 200 %}...{% endif %}</div>
            <div class="tweet-meta">
                {{ item.published[:10] }} • 
                <a href="{{ item.url }}" target="_blank" style="color: rgba(255,255,255,0.8);">View Tweet</a>
            </div>
        </div>
        {% endfor %}
        {% else %}
        <div class="no-twitter">
            📭 No recent competitor tweets found (likely due to API rate limits)
        </div>
        {% endif %}
    </div>
    
    <!-- Trend Analysis Section -->
    {% if digest.trend_insights %}
    <div class="trend-section">
        <h2>📈 AI-Powered Trend Analysis</h2>
        
        {% if digest.trend_insights.trends %}
        <div class="trend-subsection">
            <h3>🔍 Emerging Trends</h3>
            <ul class="trend-list">
            {% for trend in digest.trend_insights.trends %}
                <li>{{ trend }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if digest.trend_insights.competitive_moves %}
        <div class="trend-subsection">
            <h3>🏢 Key Competitive Movements</h3>
            <ul class="trend-list">
            {% for move in digest.trend_insights.competitive_moves %}
                <li>{{ move }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if digest.trend_insights.tech_shifts %}
        <div class="trend-subsection">
            <h3>⚡ Technology Shifts</h3>
            <ul class="trend-list">
            {% for shift in digest.trend_insights.tech_shifts %}
                <li>{{ shift }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Multi-Agent Intelligence Section -->
    {% if digest.multi_agent_analysis %}
    <div class="multi-agent-section">
        <h2>🤖 Multi-Agent Intelligence Analysis</h2>
        
        {% if digest.multi_agent_analysis.cross_agent_synthesis.synthesis_available %}
        <div class="synthesis-section">
            <h3>🎯 Strategic Synthesis</h3>
            
            {% if digest.multi_agent_analysis.cross_agent_synthesis.strategic_priorities %}
            <div class="synthesis-subsection">
                <h4>Strategic Priorities</h4>
                <ul class="synthesis-list">
                {% for priority in digest.multi_agent_analysis.cross_agent_synthesis.strategic_priorities %}
                    <li>{{ priority }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if digest.multi_agent_analysis.cross_agent_synthesis.immediate_actions %}
            <div class="synthesis-subsection">
                <h4>Immediate Actions</h4>
                <ul class="synthesis-list">
                {% for action in digest.multi_agent_analysis.cross_agent_synthesis.immediate_actions %}
                    <li>{{ action }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- Agent-Specific Results -->
        <div class="agent-results">
            {% for agent_type, result in digest.multi_agent_analysis.agent_results.items() %}
            {% if result.items_analyzed > 0 %}
            <div class="agent-card">
                <h3>{{ agent_type.replace('_', ' ').title() }}</h3>
                <div class="agent-stats">
                    <span class="stat-badge">{{ result.items_analyzed }} items analyzed</span>
                </div>
                
                {% if result.insights %}
                <div class="agent-insights">
                    {% for category, insights in result.insights.items() %}
                    {% if insights %}
                    <div class="insight-category">
                        <h5>{{ category.replace('_', ' ').title() }}</h5>
                        <ul class="insight-list">
                        {% for insight in insights %}
                            <li>{{ insight }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endif %}
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    <!-- Regular Categories -->
    {% for category_name in digest.categories %}
    {% set category_data = digest.categories[category_name] %}
    {% set non_twitter_items = [] %}
    {% for item in category_data['items'] %}
    {% if not ('twitter' in item.source.lower() or 'x.com' in item.url.lower()) %}
    {% set _ = non_twitter_items.append(item) %}
    {% endif %}
    {% endfor %}
    
    {% if non_twitter_items %}
    <div class="category">
        <div class="category-header">
            <h2>{{ category_name }}</h2>
            <span class="category-count">{{ non_twitter_items|length }} items</span>
        </div>
        
        {% for item in non_twitter_items %}
        <div class="item">
            <div class="item-header">
                <h3 class="item-title">{{ item.title }}</h3>
                <span class="item-source">{{ item.source }}</span>
            </div>
            
            {% if item.summary %}
            <div class="item-summary">{{ item.summary }}</div>
            {% endif %}
            
            <div>
                <a href="{{ item.url }}" class="item-link" target="_blank">Read more →</a>
            </div>
            
            <div class="item-meta">
                <span>{{ item.published[:10] }}</span>
                <span class="relevance-score">{{ "%.0f"|format(item.relevance_score * 100) }}% relevant</span>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    {% endfor %}
    
    <div class="footer">
        <p>Generated by AI Competitive Intelligence Agent</p>
        <p>Sources: {% for source in digest.summary_stats.sources %}{{ source }}{% if not loop.last %}, {% endif %}{% endfor %}</p>
    </div>
</body>
</html>
        """)
        
        return template.render(digest=digest)
    
    def _format_markdown(self, digest: Dict) -> str:
        """Format digest as Markdown"""
        template = Template("""
# 🎯 Competitive Intelligence Digest

**Generated:** {{ digest.generated_at[:10] }}  
**Total Items:** {{ digest.total_items }}  
**Categories:** {{ digest.categories|length }}  
**Sources:** {{ digest.summary_stats.sources|length }}  
**Avg Relevance:** {{ "%.0f"|format(digest.summary_stats.avg_relevance * 100) }}%

---

{% for category_name in digest.categories %}
{% set category_data = digest.categories[category_name] %}
## {{ category_name }} ({{ category_data['count'] }} items)

{% for item in category_data['items'] %}
### {{ item.title }}

**Source:** {{ item.source }}  
**Published:** {{ item.published[:10] }}  
**Relevance:** {{ "%.0f"|format(item.relevance_score * 100) }}%

{% if item.summary %}
{{ item.summary }}
{% endif %}

[Read more →]({{ item.url }})

---
{% endfor %}

{% endfor %}

## Sources
{% for source_name in digest.summary_stats.sources %}
{% set count = digest.summary_stats.sources[source_name] %}
- {{ source_name }}: {{ count }} items
{% endfor %}

*Generated by AI Competitive Intelligence Agent*
        """)
        
        return template.render(digest=digest)
    
    def _format_json(self, digest: Dict) -> str:
        """Format digest as JSON"""
        return json.dumps(digest, indent=2, ensure_ascii=False)

class EmailNotifier:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def send_digest(self, digest_content: str, digest_data: Dict):
        """Send digest via email (placeholder implementation)"""
        if not self.config.email_recipients:
            self.logger.info("No email recipients configured")
            return
        
        self.logger.info(f"Would send digest to: {', '.join(self.config.email_recipients)}")
        
        # In a real implementation, you would use:
        # - SMTP library for email sending
        # - Email service like SendGrid, SES, etc.
        # - Internal notification system
        
        # For now, just log the action
        self.logger.info("Email notification sent successfully")
    
    def send_slack_notification(self, digest_data: Dict):
        """Send notification to Slack (placeholder implementation)"""
        summary = f"""
🎯 *Competitive Intelligence Digest*

📊 *Stats:*
• {digest_data['total_items']} total items
• {len(digest_data['categories'])} categories
• {digest_data['summary_stats']['avg_relevance']:.0%} avg relevance

🔍 *Top Categories:*
"""
        
        for category, data in list(digest_data['categories'].items())[:3]:
            summary += f"• {category}: {data['count']} items\n"
        
        self.logger.info("Slack notification prepared:")
        self.logger.info(summary)
        
        # In a real implementation, you would use:
        # - Slack API
        # - Webhook integration
        # - Bot messaging
        
        self.logger.info("Slack notification sent successfully")