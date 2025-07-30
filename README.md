# AI Competitive Intelligence Agent

An AI-powered agent that monitors competitors, industry news, and AI developments to create automated competitive intelligence digests for Aircall.

## Features

- **Comprehensive source monitoring**: 8 RSS feeds, 21 Twitter accounts, covering industry news, competitors, and conversation intelligence tools
- **AI-powered processing**: Content categorization, relevance scoring, and OpenAI summarization tailored for Aircall's business
- **Advanced categorization**: 8 specialized categories including Competitor Intelligence, Conversation Intelligence, AI Voice Technology, and more
- **Weekly digest generation**: Beautiful HTML newsletters optimized for internal distribution
- **Aircall-specific intelligence**: Focused on UCaaS, CCaaS, cloud communications, and sales/support technology
- **Competitive monitoring**: Tracks RingCentral, 8x8, Dialpad, Vonage, Twilio, Five9, Genesys, Zoom, Microsoft Teams, Slack
- **Conversation intelligence tracking**: Monitors Gong, Chorus.ai, Salesloft, Modjo, and other real-time assistance tools
- **Regulatory compliance monitoring**: Tracks FCC, ETSI, IETF, and telecommunications regulations

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the agent**:
```bash
python main.py
```

## Configuration

### API Keys Required

- **OpenAI API Key**: For AI-powered content summarization
- **Twitter Bearer Token**: For monitoring Twitter/X accounts (optional)

### Configuration File

Edit `config.json` to customize:

- **Web sources**: RSS feeds and websites to monitor
- **Twitter usernames**: Accounts to track for announcements
- **Categories**: Content categorization and keywords
- **Processing settings**: Relevance thresholds, summary lengths
- **Output format**: HTML, Markdown, or JSON

### Comprehensive Source Coverage

The agent monitors:
- **Industry News**: TechCrunch, VentureBeat, No Jitter, UC Today, ZDNet, Hacker News, Crunchbase News
- **Direct Competitors**: RingCentral, 8x8, Dialpad, Vonage, Twilio, Five9, Genesys, Zoom, Microsoft Teams, Slack
- **Conversation Intelligence**: Gong, Chorus.ai, Salesloft, Modjo, LivePerson, Uniphore, and 10+ other CI vendors
- **Product Discovery**: Product Hunt for new launches and innovations
- **Social Intelligence**: 21 Twitter accounts covering competitors, AI companies, and industry leaders

## Usage

### Basic Usage
```bash
python main.py                    # Run with default settings
python main.py --config custom.json  # Use custom config
python main.py --output report.html  # Custom output file
python main.py --dry-run            # Test without sending notifications
python main.py --force              # Force run even if recently executed
```

### Scheduling

Set up automated runs with cron:
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/agent && python main.py
```

### Output Formats

- **HTML**: Beautiful newsletter format (default)
- **Markdown**: Clean text format for documentation
- **JSON**: Structured data for integration

## Content Categories

1. **Competitor Intelligence**: Direct competitors, funding, partnerships, strategic moves
2. **Conversation Intelligence & Real-Time Assistance**: Sales enablement, call coaching, conversation analytics
3. **AI Voice Technology**: Voice AI, conversational AI, speech recognition, NLP
4. **UCaaS & Cloud Communications**: Unified communications, VoIP, WebRTC, CPaaS
5. **Contact Center & Customer Support**: CCaaS, customer experience, agent assistance
6. **Sales & CRM Technology**: Sales automation, customer intelligence, revenue operations
7. **Regulatory & Compliance**: FCC, ETSI, IETF, data privacy, telecommunications law
8. **Industry Analysis & Reports**: Gartner, Forrester, market research, analyst insights

## Architecture

- **Sources** (`src/sources.py`): Web scraping and social media monitoring
- **Processor** (`src/processor.py`): AI-powered content analysis
- **Formatter** (`src/formatter.py`): Digest generation and styling
- **Agent** (`src/agent.py`): Main orchestration and state management

## Customization

### Adding New Sources

Add to `config.json`:
```json
{
  "name": "New Source",
  "url": "https://example.com/feed",
  "type": "rss",
  "enabled": true,
  "keywords": ["AI", "voice", "sales"]
}
```

### Custom Categories

Define new categories with keywords:
```json
{
  "name": "Custom Category",
  "keywords": ["keyword1", "keyword2"],
  "priority": 1
}
```

### Relevance Tuning

Adjust relevance scoring in `src/processor.py`:
- High-value keywords: +0.3 points
- Medium-value keywords: +0.2 points
- Low-value keywords: +0.1 points

## Monitoring

The agent logs all activities and maintains state in:
- **Log files**: `agent_YYYYMMDD.log`
- **State file**: `agent_state.json`

## Notifications

Configure email and Slack notifications:
- Add email recipients to `config.json`
- Set up Slack webhook in `.env`

## Security

- Store API keys in `.env` file (not in version control)
- Use environment variables for sensitive configuration
- Implement rate limiting for API calls
- Validate all external content

## License

Internal use for Aircall competitive intelligence.