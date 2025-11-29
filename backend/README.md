# Tourism Category Filtering Algorithm with AI City Inference

A sophisticated Python system that filters and ranks tourism categories (places, activities, dining) based on city characteristics, travel dates, trip type, and budget. Features intelligent AI-powered city inference for destinations not in the database.

## 🌟 Features

- **Intelligent City Lookup**: Fast database lookup for ~380 cities
- **AI City Inference**: Automatic Claude-powered inference for unknown cities
- **Smart Filtering**: Multi-dimensional filtering based on:
  - Geographic requirements (coastal, urban, mountain, etc.)
  - Seasonal compatibility
  - Trip type matching (romantic, family, solo, etc.)
  - Budget alignment
  - Weather requirements
- **Relevance Scoring**: 0-100 scoring system that ranks categories by relevance
- **Hemisphere-Aware**: Automatically adjusts seasons for Southern Hemisphere
- **Special Period Detection**: Christmas, Easter, summer holidays, etc.
- **Caching**: Caches AI-inferred cities to avoid repeated API calls

## 📋 Requirements

```bash
pip install anthropic --break-system-packages
```

You'll also need:
- Python 3.8+
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)
- `cities.json` - Database of ~380 cities with tourism tags
- `categories.json` - Database of tourism categories

## 🚀 Quick Start

### Basic Usage

```python
from tourism_filter import CityDatabase, filter_categories, load_categories

# Initialize
city_db = CityDatabase('cities.json')
categories = load_categories('categories.json')

# Define user input
user_input = {
    "destination": {
        "city": "Prague",
        "country": "Czech Republic"
    },
    "dates": {
        "start": "2025-12-18",
        "end": "2025-12-25"
    },
    "trip_type": "romantic_couple",  # solo_trip, romantic_couple, family_young_children, etc.
    "budget": "mid_range"  # budget, mid_range, luxury
}

# Filter categories
results = filter_categories(
    categories,
    user_input["destination"]["city"],
    user_input["destination"]["country"],
    user_input,
    city_db
)

# Access results
print(f"Top places: {[p['name'] for p in results['places'][:5]]}")
print(f"Top activities: {[a['name'] for a in results['activities'][:5]]}")
```

### Run Examples

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run example scenarios
python example_usage.py
```

This will demonstrate:
1. **Prague** - Known city from database (winter romantic trip)
2. **Tokyo** - Known city (spring family trip)
3. **Plovdiv** - Unknown city using AI inference (summer budget trip)
4. **Valparaiso** - Unknown city using AI inference (summer solo trip)

## 🏗️ Architecture

### Core Components

1. **CityDatabase** (`tourism_filter.py`)
   - Loads and indexes city database
   - Handles lookups with fuzzy matching
   - Falls back to AI inference for unknown cities
   - Caches AI results

2. **Season Calculation** (`tourism_filter.py`)
   - Hemisphere-aware season detection
   - Special period identification (Christmas, Easter, etc.)
   - Date context generation

3. **Filtering Engine** (`tourism_filter.py`)
   - Hard filters (must-pass requirements)
   - Soft scoring (relevance ranking)
   - Fallback mechanisms

4. **AI Inference** (`tourism_filter.py`)
   - Uses Claude Sonnet 4.5 for city analysis
   - Structured output with confidence levels
   - Strict tag vocabulary enforcement

## 📊 Data Structures

### User Input

```python
{
    "destination": {
        "city": str,        # City name
        "country": str      # Country name
    },
    "dates": {
        "start": str,       # YYYY-MM-DD
        "end": str          # YYYY-MM-DD
    },
    "trip_type": str,       # Enum: solo_trip, romantic_couple, couple_travel,
                            #       family_young_children, family_teens,
                            #       group_friends, business_travel
    "budget": str           # Enum: budget, mid_range, luxury
}
```

### Output Structure

```python
{
    "city_info": {
        "city": str,
        "country": str,
        "from_database": bool,                    # True if from DB, False if AI-inferred
        "inference_confidence": str|None,         # "high", "medium", "low", or None
        "city_tags": {
            "geo_type": List[str],                # ["urban", "riverside"]
            "geo_region": List[str],              # ["eastern_europe"]
            "climate_type": List[str],            # ["continental"]
            "tourism_characteristics": List[str], # ["historical_city", "cultural_hub"]
            "special_features": List[str]         # ["unesco_sites", "nightlife_hub"]
        }
    },
    "date_context": {
        "season": str,              # "spring", "summer", "autumn", "winter"
        "adjusted_season": str,     # Hemisphere-adjusted season
        "special_periods": List[str], # ["christmas_period", "easter"]
        "hemisphere": str,          # "northern" or "southern"
        "month": int                # 1-12
    },
    "places": List[{
        "name": str,
        "parent_category": str,
        "relevance_score": int,           # 0-100
        "search_query_template": str,
        "description": str
    }],
    "activities": List[...],              # Same structure as places
    "dining": {
        "cuisines": List[...],
        "formats": List[...],
        "dietary": List[...]
    },
    "excluded_count": int,
    "excluded_examples": List[{           # Sample of filtered-out categories
        "name": str,
        "parent": str,
        "reason": str
    }]
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_tourism_filter.py
```

Tests cover:
- ✅ Season calculation (both hemispheres)
- ✅ Special period detection
- ✅ Date context generation
- ✅ Hard filter logic (trip type, budget, geo, weather)
- ✅ Relevance scoring algorithm
- ✅ City database operations
- ✅ Category loading

## 🎯 Filtering Logic

### Hard Filters (Must Pass)

Categories are **excluded** if they fail any of these:

1. **Trip Type Exclusion**: Category explicitly excludes the trip type
2. **Budget Exclusion**: Category explicitly excludes the budget level
3. **Geographic Mismatch**: Required geography doesn't match city
   - Example: Surfing requires coastal/island, Prague is urban/riverside
4. **Regional Mismatch**: Required region doesn't match city's region
   - Example: Temples require Asia, Paris is in Europe
5. **Infrastructure**: Required infrastructure level doesn't match
6. **Weather Requirements**: Season doesn't support activity
   - Example: Warm weather activities in winter (non-tropical cities)

### Relevance Scoring (0-100)

Categories that pass hard filters are scored:

| Factor | Points | Description |
|--------|--------|-------------|
| Trip Type Match | +15 | Category is ideal for the trip type |
| Budget Match | +10 | Category supports the budget level |
| Perfect Season | +20 | Category's ideal season matches travel date |
| All-Season | +10 | Category works year-round |
| Special Period | +15 | Matches special time (Christmas, Easter, etc.) |
| Tourism Characteristics | +5 each (max +20) | City's tourism features align with category |
| Special Features | +10 each (max +20) | City's unique features match category needs |
| Bucket List | +5 | Category is a "must-do" experience |
| Instagram Worthy | +3 | Category is photogenic/shareable |

**Maximum Score**: 100 (capped)

## 🤖 AI City Inference

When a city is not in the database, the system:

1. **Prompts Claude** with strict tag vocabulary
2. **Receives structured JSON** with city characteristics
3. **Includes confidence level** (high/medium/low)
4. **Caches result** to avoid repeated API calls
5. **Falls back to generic data** if AI fails

### Example AI Inference Output

```json
{
  "city": "Plovdiv",
  "country": "Bulgaria",
  "region": "eastern_europe",
  "tags": {
    "geo_type": ["urban", "riverside"],
    "geo_region": ["eastern_europe"],
    "climate_type": ["continental"],
    "weather_characteristics": ["snowy_winters", "extreme_heat_summer"],
    "seasonal_features": ["summer_festivals", "autumn_foliage"],
    "infrastructure": ["developed"],
    "tourism_characteristics": ["historical_city", "cultural_hub", "backpacker_friendly"],
    "special_features": ["unesco_sites", "ancient_ruins"]
  },
  "confidence": "high",
  "from_database": false
}
```

## 📈 Performance Optimization

- **City Lookup**: O(1) hash-based lookup
- **Fuzzy Matching**: O(n) only when exact match fails
- **AI Caching**: Repeated queries for same city use cached data
- **Category Pre-indexing**: Categories loaded once at startup

## 🛠️ Advanced Usage

### Custom Confidence Thresholds

```python
results = filter_categories(...)

# Check confidence before using results
if results['city_info']['inference_confidence'] == 'low':
    print("Warning: Low confidence city data. Results may be less accurate.")
```

### Accessing Excluded Categories

```python
# See why categories were filtered out
for excluded in results['excluded_examples']:
    print(f"{excluded['name']}: {excluded['reason']}")
```

### Filtering Specific Lists

```python
# Get only high-scoring places
top_places = [p for p in results['places'] if p['relevance_score'] >= 50]

# Get only activities suitable for families
family_activities = [
    a for a in results['activities'] 
    if 'family_oriented' in categories_lookup[a['name']]['tags'].get('age_appropriate', [])
]
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for AI inference
export ANTHROPIC_API_KEY='your-api-key-here'
```

### File Paths

Update paths in your code if files are in different locations:

```python
city_db = CityDatabase('/path/to/cities.json')
categories = load_categories('/path/to/categories.json')
```

## 📝 Error Handling

The system handles errors gracefully:

- **Unknown City + API Failure**: Returns generic fallback city data
- **Missing Database Files**: Raises clear error messages
- **Invalid User Input**: Continues with best-effort filtering
- **Empty Results**: Automatically provides fallback generic categories

## 🚨 Limitations

1. **AI Inference Accuracy**: Unknown cities depend on Claude's knowledge (usually very accurate)
2. **API Costs**: Each unknown city requires an API call (~1000 tokens)
3. **Database Coverage**: Only ~380 cities pre-loaded
4. **Tag Vocabulary**: Fixed set of tags (can't infer new characteristics)

## 📚 Examples in the Wild

### Scenario 1: Romantic Winter Weekend in Prague

```python
user_input = {
    "destination": {"city": "Prague", "country": "Czech Republic"},
    "dates": {"start": "2025-12-18", "end": "2025-12-25"},
    "trip_type": "romantic_couple",
    "budget": "mid_range"
}
```

**Top Results**:
1. Christmas Markets (Score: 35) - Special period match
2. Historical Old Town (Score: 28) - Perfect for romantic couples
3. Castles & Palaces (Score: 25) - Historical city feature

### Scenario 2: Family Trip to Tokyo in Spring

```python
user_input = {
    "destination": {"city": "Tokyo", "country": "Japan"},
    "dates": {"start": "2025-04-01", "end": "2025-04-08"},
    "trip_type": "family_young_children",
    "budget": "mid_range"
}
```

**Top Results**:
1. Theme Parks (Score: 40) - Family-oriented, special features match
2. Cherry Blossom Viewing (Score: 35) - Perfect season
3. Interactive Museums (Score: 28) - Family-friendly

## 🤝 Contributing

Potential improvements:
- Add more cities to database
- Expand tag vocabulary
- Implement multi-city trip support
- Add real-time price data integration
- Support custom user preferences

## 📄 License

This is a demonstration project created for educational purposes.

## 🙏 Acknowledgments

- Anthropic Claude API for AI city inference
- Tourism data structures based on industry standards
- Hemisphere-aware season calculation inspired by travel planning systems
