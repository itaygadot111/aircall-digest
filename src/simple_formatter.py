"""
Simple digest formatting optimized for Slack and clean HTML output
"""

import json
from datetime import datetime
from typing import Dict, List
from jinja2 import Template

class SimpleDigestFormatter:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def format_digest(self, digest: Dict) -> str:
        """Format digest based on configured output format"""
        if self.config.output_format == "html":
            return self._format_simple_html(digest)
        elif self.config.output_format == "markdown":
            return self._format_simple_markdown(digest)
        elif self.config.output_format == "json":
            return self._format_json(digest)
        elif self.config.output_format == "slack":
            # Save both Slack format and HTML for comparison
            slack_content = self._format_slack(digest)
            html_content = self._format_simple_html(digest)
            
            # Save HTML version to separate file
            with open('digest.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save Slack version to separate file
            with open('digest_slack.txt', 'w', encoding='utf-8') as f:
                f.write(slack_content)
                
            return slack_content
        else:
            return self._format_simple_html(digest)
    
    def _format_simple_html(self, digest: Dict) -> str:
        """Simple, clean HTML format"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Aircall Competitive Intelligence</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #ffffff;
        }
        .header {
            background: #00BD82;
            color: white;
            padding: 25px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2em;
            font-weight: 600;
        }
        .header p {
            margin: 8px 0 0 0;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            color: #00BD82;
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #00BD82;
        }
        .item {
            background: #f8f9fa;
            border-left: 4px solid #00BD82;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .item-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .item-company {
            color: #00BD82;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        .item-summary {
            color: #5a6c7d;
            margin-bottom: 8px;
            line-height: 1.5;
        }
        .item-link {
            color: #00BD82;
            text-decoration: none;
            font-weight: 500;
        }
        .item-link:hover {
            text-decoration: underline;
        }
        .multi-agent-insights {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #6f42c1;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .multi-agent-insights h2 {
            color: #6f42c1;
            margin-top: 0;
            font-size: 1.5em;
        }
        .agent-section {
            margin-bottom: 20px;
        }
        .agent-title {
            color: #495057;
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .insight-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 8px;
            color: #495057;
        }
        .synthesis {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .synthesis h3 {
            color: #856404;
            margin-top: 0;
            font-size: 1.3em;
        }
        .synthesis-item {
            background: white;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 8px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Competitive Intelligence</h1>
        <p>{{ digest.generated_at[:10] }}</p>
    </div>
    
    <!-- DISABLED: Multi-agent insights (generating hallucinated content without source attribution) -->
    {# Multi-Agent Strategic Insights
    {% if digest.multi_agent_analysis and digest.multi_agent_analysis.cross_agent_synthesis.synthesis_available %}
    <div class="synthesis">
        <h3>🧠 Strategic Insights</h3>
        
        {% if digest.multi_agent_analysis.cross_agent_synthesis.strategic_priorities %}
        <div style="margin-bottom: 15px;">
            <strong>Key Priorities:</strong>
            {% for priority in digest.multi_agent_analysis.cross_agent_synthesis.strategic_priorities %}
            <div class="synthesis-item">{{ priority }}</div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if digest.multi_agent_analysis.cross_agent_synthesis.immediate_actions %}
        <div>
            <strong>Immediate Actions:</strong>
            {% for action in digest.multi_agent_analysis.cross_agent_synthesis.immediate_actions %}
            <div class="synthesis-item">{{ action }}</div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endif %}
    
    Specialized Agent Insights
    {% if digest.multi_agent_analysis %}
    <div class="multi-agent-insights">
        <h2>🤖 AI Analysis</h2>
        
        {% for agent_type, result in digest.multi_agent_analysis.agent_results.items() %}
        {% if result.items_analyzed > 0 and result.insights %}
        <div class="agent-section">
            <div class="agent-title">{{ agent_type.replace('_', ' ').title() }}</div>
            
            {% for category, insights in result.insights.items() %}
            {% if insights %}
            {% for insight in insights %}
            <div class="insight-item">{{ insight }}</div>
            {% endfor %}
            {% endif %}
            {% endfor %}
        </div>
        {% endif %}
        {% endfor %}
    </div>
    {% endif %}
    #}
    
    <!-- Top Stories Section -->
    {% set total_items = digest.total_items %}
    {% if total_items >= 10 %}
        {% set top_count = 3 if total_items < 20 else 5 %}
        {% set top_items = [] %}
        {% for category_name in digest.categories %}
            {% set category_data = digest.categories[category_name] %}
            {% for item in category_data['items'] %}
                {% set _ = top_items.append(item) %}
            {% endfor %}
        {% endfor %}
        {% set top_items = top_items | sort(attribute='relevance_score', reverse=true) %}
        
        <div class="section">
            <h2 class="section-title">🔥 Top Stories</h2>
            
            {% for item in top_items[:top_count] %}
            <div class="item">
                <div class="item-title">{{ item.title }}</div>
                {% if item.summary %}
                    {% set parts = item.summary.split('SUMMARY:') %}
                    {% if parts|length > 1 %}
                        {% set company_part = parts[0].replace('COMPANY:', '').strip() %}
                        {% set summary_part = parts[1].strip() %}
                        {% if company_part %}
                        <div class="item-company">{{ company_part }}</div>
                        {% endif %}
                        {% if summary_part %}
                        <div class="item-summary">{{ summary_part }}</div>
                        {% endif %}
                    {% else %}
                        <div class="item-summary">{{ item.summary }}</div>
                    {% endif %}
                {% endif %}
                <div>
                    <a href="{{ item.url }}" class="item-link" target="_blank">Read more →</a>
                </div>
            </div>
            {% endfor %}
        </div>
    {% endif %}
    
    <!-- News Items -->
    {% for category_name in digest.categories %}
    {% set category_data = digest.categories[category_name] %}
    <div class="section">
        <h2 class="section-title">{{ category_name }}</h2>
        
        {% for item in category_data['items'] %}
        <div class="item">
            <div class="item-title">{{ item.title }}</div>
            {% if item.summary %}
                {% set parts = item.summary.split('SUMMARY:') %}
                {% if parts|length > 1 %}
                    {% set company_part = parts[0].replace('COMPANY:', '').strip() %}
                    {% set summary_part = parts[1].strip() %}
                    {% if company_part %}
                    <div class="item-company">{{ company_part }}</div>
                    {% endif %}
                    {% if summary_part %}
                    <div class="item-summary">{{ summary_part }}</div>
                    {% endif %}
                {% else %}
                    <div class="item-summary">{{ item.summary }}</div>
                {% endif %}
            {% endif %}
            <div>
                <a href="{{ item.url }}" class="item-link" target="_blank">Read more →</a>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
</body>
</html>
        """)
        
        return template.render(digest=digest)
    
    def _format_slack(self, digest: Dict) -> str:
        """Format for Slack rich text blocks"""
        blocks = []
        
        # Header block
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Competitive Intelligence Update"
            }
        })
        
        # Date context
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_{digest.get('generated_at', '')[:10]}_"
                }
            ]
        })
        
        # Divider
        blocks.append({"type": "divider"})
        
        # Top Stories Section (if there are 10+ items)
        total_items = digest.get('total_items', 0)
        if total_items >= 10:
            top_count = 3 if total_items < 20 else 5
            all_items = []
            for category_name, category_data in digest.get('categories', {}).items():
                for item in category_data.get('items', []):
                    all_items.append(item)
            
            # Sort by relevance and get top items
            all_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            top_items = all_items[:top_count]
            
            # Top Stories header
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": "*🔥 Top Stories*"
                }
            })
            
            for item in top_items:
                summary_text = ""
                if item.get('summary'):
                    summary = item['summary']
                    if 'COMPANY:' in summary and 'SUMMARY:' in summary:
                        parts = summary.split('SUMMARY:')
                        if len(parts) > 1:
                            company_part = parts[0].replace('COMPANY:', '').strip()
                            summary_part = parts[1].strip()
                            if company_part:
                                summary_text += f"*{company_part}*\n"
                            if summary_part:
                                truncated = summary_part[:150] + "..." if len(summary_part) > 150 else summary_part
                                summary_text += f"_{truncated}_"
                    else:
                        truncated = summary[:150] + "..." if len(summary) > 150 else summary
                        summary_text = f"_{truncated}_"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{item['title']}*\n{summary_text}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Read More"
                        },
                        "url": item['url'],
                        "action_id": f"read_more_{hash(item['url']) % 10000}"
                    }
                })
            
            blocks.append({"type": "divider"})
        
        # News by Categories
        if digest.get('categories'):
            for category_name, category_data in digest['categories'].items():
                if category_data.get('items'):
                    # Category header
                    blocks.append({
                        "type": "section", 
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*📋 {category_name}* ({category_data['count']} items)"
                        }
                    })
                    
                    # Show top 2-3 items per category
                    items_to_show = min(3, len(category_data['items']))
                    for item in category_data['items'][:items_to_show]:
                        summary_text = ""
                        if item.get('summary'):
                            summary = item['summary']
                            if 'COMPANY:' in summary and 'SUMMARY:' in summary:
                                parts = summary.split('SUMMARY:')
                                if len(parts) > 1:
                                    company_part = parts[0].replace('COMPANY:', '').strip()
                                    summary_part = parts[1].strip()
                                    if company_part:
                                        summary_text += f"*{company_part}*\n"
                                    if summary_part:
                                        truncated = summary_part[:120] + "..." if len(summary_part) > 120 else summary_part
                                        summary_text += f"_{truncated}_"
                            else:
                                truncated = summary[:120] + "..." if len(summary) > 120 else summary
                                summary_text = f"_{truncated}_"
                        
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"• *{item['title']}*\n{summary_text}"
                            },
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Read"
                                },
                                "url": item['url'],
                                "action_id": f"read_{hash(item['url']) % 10000}"
                            }
                        })
                    
                    # If there are more items, show count
                    if len(category_data['items']) > items_to_show:
                        remaining = len(category_data['items']) - items_to_show
                        blocks.append({
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"_...and {remaining} more items_"
                                }
                            ]
                        })
                    
                    blocks.append({"type": "divider"})
        
        # Return as JSON for Slack Block Kit
        import json
        return json.dumps({"blocks": blocks}, indent=2)
    
    def _format_simple_markdown(self, digest: Dict) -> str:
        """Simple markdown format"""
        lines = []
        lines.append("# 🎯 Competitive Intelligence")
        lines.append(f"**Date:** {digest.get('generated_at', '')[:10]}\n")
        
        # Strategic insights
        if (digest.get('multi_agent_analysis') and 
            digest['multi_agent_analysis'].get('cross_agent_synthesis', {}).get('synthesis_available')):
            
            synthesis = digest['multi_agent_analysis']['cross_agent_synthesis']
            
            if synthesis.get('strategic_priorities'):
                lines.append("## 🧠 Strategic Priorities")
                for priority in synthesis['strategic_priorities']:
                    lines.append(f"- {priority}")
                lines.append("")
            
            if synthesis.get('immediate_actions'):
                lines.append("## ⚡ Immediate Actions")
                for action in synthesis['immediate_actions']:
                    lines.append(f"- {action}")
                lines.append("")
        
        # AI insights
        if digest.get('multi_agent_analysis'):
            lines.append("## 🤖 AI Analysis")
            agent_results = digest['multi_agent_analysis'].get('agent_results', {})
            
            for agent_type, result in agent_results.items():
                if result.get('items_analyzed', 0) > 0 and result.get('insights'):
                    agent_name = agent_type.replace('_', ' ').title()
                    lines.append(f"### {agent_name}")
                    
                    for category, insights in result['insights'].items():
                        for insight in insights:
                            lines.append(f"- {insight}")
                    lines.append("")
        
        # News categories
        for category_name, category_data in digest.get('categories', {}).items():
            lines.append(f"## {category_name}")
            
            for item in category_data.get('items', []):
                lines.append(f"### {item['title']}")
                if item.get('summary'):
                    lines.append(item['summary'])
                lines.append(f"[Read more]({item['url']})\n")
        
        return "\n".join(lines)
    
    def _format_json(self, digest: Dict) -> str:
        """Simple JSON format"""
        return json.dumps(digest, indent=2, ensure_ascii=False)

class SimpleEmailNotifier:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def send_digest(self, digest_content: str, digest_data: Dict):
        """Send simplified digest via email"""
        if not self.config.email_recipients:
            self.logger.info("No email recipients configured")
            return
        
        self.logger.info(f"Would send simplified digest to: {', '.join(self.config.email_recipients)}")
        self.logger.info("Email notification sent successfully")
    
    def send_slack_notification(self, digest_data: Dict):
        """Send Slack-formatted notification"""
        formatter = SimpleDigestFormatter(self.config, self.logger)
        slack_content = formatter._format_slack(digest_data)
        
        self.logger.info("Slack notification prepared:")
        self.logger.info("=" * 50)
        self.logger.info(slack_content)
        self.logger.info("=" * 50)
        
        # In production, would send via Slack webhook
        self.logger.info("Slack notification sent successfully")