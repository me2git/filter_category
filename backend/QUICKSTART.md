# Quick Start Guide: Tourism Category Filtering

Get started with the Tourism Category Filtering Algorithm in 5 minutes!

## 🚀 Installation

```bash
# Install dependencies
pip install anthropic --break-system-packages

# Optional: Set API key for AI city inference
export ANTHROPIC_API_KEY='your-api-key-here'
```

## 📦 Files You Need

Make sure you have:
- `tourism_filter.py` - Main algorithm module
- `cities.json` - Database of ~380 cities
- `categories.json` - Database of tourism categories

## 🎯 Run the Demo (No API Key Required)

Try the simple demo that uses only database cities:

```bash
python simple_demo.py
```

This will show you filtering results for:
- Prague (romantic winter trip)
- Bali (family beach holiday)
- New York (solo budget adventure)

## 🧪 Run Tests

Verify everything works correctly:

```bash
python test_tourism_filter.py
```

Expected output: `24 tests passed`

## 💡 Basic Usage

### 1. Import and Initialize

```python
from tourism_filter import CityDatabase, filter_categories, load_categories

# Load databases
city_db = CityDatabase('cities.json')
categories = load_categories('categories.json')
```

### 2. Define User Input

```python
user_input = {
    "destination": {
        "city": "Prague",
        "country": "Czech Republic"
    },
    "dates": {
        "start": "2025-12-18",
        "end": "2025-12-25"
    },
    "trip_type": "romantic_couple",  # See options below
    "budget": "mid_range"            # budget, mid_range, luxury
}
```

**Trip Type Options:**
- `solo_trip`
- `romantic_couple`
- `couple_travel`
- `family_young_children`
- `family_teens`
- `group_friends`
- `business_travel`

### 3. Filter Categories

```python
results = filter_categories(
    categories,
    user_input["destination"]["city"],
    user_input["destination"]["country"],
    user_input,
    city_db
)
```

### 4. Access Results

```python
# City information
print(f"City: {results['city_info']['city']}")
print(f"From database: {results['city_info']['from_database']}")

# Top places
for place in results['places'][:5]:
    print(f"- {place['name']} (Score: {place['relevance_score']})")

# Top activities
for activity in results['activities'][:5]:
    print(f"- {activity['name']} (Score: {activity['relevance_score']})")

# Dining options
for cuisine in results['dining']['cuisines'][:5]:
    print(f"- {cuisine['name']} (Score: {cuisine['relevance_score']})")
```

## 🤖 Testing AI City Inference

For cities not in the database, the system uses AI inference:

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run examples with unknown cities
python example_usage.py
```

This demonstrates:
- Plovdiv, Bulgaria (AI-inferred)
- Valparaiso, Chile (AI-inferred)

## 📊 Understanding Results

### City Info
```python
results['city_info'] = {
    'city': 'Prague',
    'country': 'Czech Republic',
    'from_database': True,              # False if AI-inferred
    'inference_confidence': None,       # 'high', 'medium', 'low' for AI
    'city_tags': {...}                  # City characteristics
}
```

### Filtered Categories
```python
results['places'] = [
    {
        'name': 'Christmas Markets',
        'parent_category': 'Seasonal Attractions',
        'relevance_score': 68,          # 0-100 score
        'search_query_template': 'christmas markets in {city}',
        'description': '...'
    },
    ...
]
```

### Exclusions
```python
results['excluded_count'] = 47
results['excluded_examples'] = [
    {
        'name': 'Surfing',
        'parent': 'Water Sports',
        'reason': 'geo_type mismatch: requires coastal/island'
    },
    ...
]
```

## 🎨 Common Use Cases

### Use Case 1: Get Top Recommendations

```python
# Get top 5 places by score
top_places = results['places'][:5]

for i, place in enumerate(top_places, 1):
    print(f"{i}. {place['name']} ({place['relevance_score']}/100)")
```

### Use Case 2: Filter by Score Threshold

```python
# Get only high-relevance categories (score >= 50)
high_relevance = [
    p for p in results['places'] 
    if p['relevance_score'] >= 50
]
```

### Use Case 3: Generate Search Queries

```python
# Generate Google/Maps search queries
city = results['city_info']['city']

for place in results['places'][:10]:
    query = place['search_query_template'].format(city=city)
    print(f"Search: {query}")
```

Output:
```
Search: christmas markets in Prague
Search: castles and palaces in Prague
Search: churches and cathedrals in Prague
...
```

### Use Case 4: Check AI Confidence

```python
# For AI-inferred cities, check confidence
if not results['city_info']['from_database']:
    confidence = results['city_info']['inference_confidence']
    
    if confidence == 'low':
        print("⚠️  Warning: Low confidence results")
    elif confidence == 'medium':
        print("ℹ️  Note: Medium confidence results")
    else:
        print("✓ High confidence results")
```

## 🔧 Advanced Usage

### Custom Category Filtering

```python
# Filter for specific parent categories
cultural_places = [
    p for p in results['places']
    if 'Cultural' in p['parent_category']
]

# Filter for budget-friendly activities
budget_activities = [
    a for a in results['activities']
    if a['relevance_score'] >= 30  # Adjust threshold
]
```

### Batch Processing Multiple Cities

```python
destinations = [
    ("Prague", "Czech Republic"),
    ("Tokyo", "Japan"),
    ("New York", "United States")
]

all_results = []

for city, country in destinations:
    results = filter_categories(categories, city, country, user_input, city_db)
    all_results.append(results)
```

### Export Results to JSON

```python
import json

# Save results
with open('filtered_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Load results
with open('filtered_results.json', 'r') as f:
    loaded_results = json.load(f)
```

## 🐛 Troubleshooting

### Error: Module 'anthropic' not found
```bash
pip install anthropic --break-system-packages
```

### Error: ANTHROPIC_API_KEY not set
```bash
# For testing without AI, use database cities only
python simple_demo.py

# For AI inference, set API key:
export ANTHROPIC_API_KEY='your-key-here'
```

### No results returned
- Check that city name and country are spelled correctly
- Try using the fuzzy matching (e.g., "NYC" might match "New York City")
- Check excluded_examples to see why categories were filtered out

### Low relevance scores
- This is normal! The algorithm is conservative
- Scores 40+ are good matches
- Scores 60+ are excellent matches
- Adjust expectations based on your use case

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Review test_tourism_filter.py** to understand edge cases
3. **Explore example_usage.py** for comprehensive examples
4. **Customize scoring weights** in `calculate_relevance_score()`
5. **Add more cities** to the database for better coverage

## 💬 Common Questions

**Q: How many cities are in the database?**
A: ~380 cities covering major tourist destinations worldwide.

**Q: What happens if my city isn't in the database?**
A: The system automatically uses AI inference (requires API key).

**Q: How accurate is the AI inference?**
A: Very accurate! Claude has excellent geographic and tourism knowledge.

**Q: Can I add my own cities to the database?**
A: Yes! Follow the JSON structure in cities.json and add new entries.

**Q: How much does AI inference cost?**
A: ~$0.002-0.005 per city inference (varies by token usage).

**Q: Can I use this commercially?**
A: Check with Anthropic's API terms and your data licensing.

## 🎉 You're Ready!

Try running the demo and experimenting with different inputs. Happy filtering!

```bash
python simple_demo.py
```
