import sys
sys.path.append('/Users/itaygadot/Documents/Agent1')
from src.config import Config
from src.processor import DigestGenerator
from src.sources import ContentItem
from datetime import datetime
from jinja2 import Template

# Create test data
config = Config.from_file('config.json')
generator = DigestGenerator(config, None)

# Create test items
items = [
    ContentItem('Test AI News', 'AI content here', 'http://example.com', 'Test Source', datetime.now(), 'General')
]
items[0].relevance_score = 0.5

# Generate digest
digest = generator.generate_digest(items)

# Simple template test
template = Template("""
<div>
    {% for category_name in digest.categories %}
    {% set category_data = digest.categories[category_name] %}
    <h2>{{ category_name }}</h2>
    <p>Count: {{ category_data.count }}</p>
    <ul>
        {% for item in category_data['items'] %}
        <li>{{ item.title }}</li>
        {% endfor %}
    </ul>
    {% endfor %}
</div>
""")

print("Test template:")
result = template.render(digest=digest)
print(result)
print("Success!")