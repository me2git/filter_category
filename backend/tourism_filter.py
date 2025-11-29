"""
Tourism Category Filtering Algorithm with AI City Inference

This module provides intelligent filtering of tourism categories based on:
- City characteristics (from database or AI inference)
- Travel dates and seasons
- Trip type and budget
- Category requirements and tags
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
from pathlib import Path
import anthropic


# ============================================================================
# PART 1: CITY LOOKUP AND AI INFERENCE
# ============================================================================

class CityDatabase:
    """Manages city data with AI inference fallback for unknown cities."""
    
    def __init__(self, cities_json_path: str):
        """Initialize city database from JSON file."""
        self.cities_path = Path(cities_json_path)
        self._load_database()
        self._inference_cache = {}  # Cache AI-inferred cities
        
    def _load_database(self):
        """Load and index city database."""
        with open(self.cities_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create fast lookup index: "city_country" -> city_data
        self.city_index = {}
        for city in data.get('cities', []):
            key = self._normalize_key(city['city'], city['country'])
            self.city_index[key] = city
        
        print(f"Loaded {len(self.city_index)} cities from database")
    
    @staticmethod
    def _normalize_key(city: str, country: str) -> str:
        """Normalize city/country for lookup."""
        return f"{city.lower().strip()}_{country.lower().strip()}"
    
    def get_city_data(self, city: str, country: str) -> Dict[str, Any]:
        """
        Get city tags from database, or use AI inference for unknown cities.
        
        Returns:
            dict: City data with tags, including metadata about source
        """
        key = self._normalize_key(city, country)
        
        # Check cache first
        if key in self._inference_cache:
            print(f"Using cached inference for {city}, {country}")
            return self._inference_cache[key]
        
        # Try exact database match
        if key in self.city_index:
            city_data = self.city_index[key].copy()
            city_data['from_database'] = True
            city_data['inference_confidence'] = None
            return city_data
        
        # Try fuzzy match (handle city name variations)
        city_lower = city.lower().strip()
        for db_key, db_city in self.city_index.items():
            db_city_name = db_city['city'].lower().strip()
            if city_lower in db_city_name or db_city_name in city_lower:
                print(f"Fuzzy match: '{city}' matched to '{db_city['city']}'")
                city_data = db_city.copy()
                city_data['from_database'] = True
                city_data['inference_confidence'] = None
                return city_data
        
        # City not found - use AI inference
        print(f"⚠️  City '{city}, {country}' not in database. Using AI inference...")
        inferred_data = self._infer_city_with_ai(city, country)
        
        # Cache the result
        self._inference_cache[key] = inferred_data
        
        return inferred_data
    
    def _infer_city_with_ai(self, city: str, country: str) -> Dict[str, Any]:
        """Use Claude to infer city tags for unknown cities."""
        
        prompt = f"""You are a travel data expert. Generate tourism tags for a city that will be used for filtering travel categories.

## CITY TO ANALYZE
City: {city}
Country: {country}

## STRICT TAG VOCABULARY

You MUST use ONLY these exact tag values. Do not invent new values.

### geo_type (select ALL that apply):
urban, rural, coastal, desert, mountain, forest, island, tropical, lakeside, riverside, volcanic, plains, limestone, arctic

### geo_region (select ONE):
east_asia, southeast_asia, south_asia, western_europe, eastern_europe, northern_europe, southern_europe, middle_east, north_africa, sub_saharan_africa, north_america, central_america, south_america, caribbean, oceania, pacific_islands, central_asia

### climate_type (select ONE):
tropical, subtropical, mediterranean, continental, oceanic, desert, semi_arid, subarctic, arctic, highland, monsoon

### weather_characteristics (select ALL that apply):
sunny_most_year, rainy_season, snowy_winters, mild_year_round, extreme_heat_summer, extreme_cold_winter, humid, dry, windy, unpredictable

### seasonal_features (select ALL that apply):
cherry_blossom, autumn_foliage, christmas_period, easter, ramadan, ski_season, summer_holidays, halloween, lunar_new_year, monsoon_avoid, northern_lights, winter_festivals, tulip_season, spring_festivals, beach_season, midnight_sun, summer_festivals, outdoor_concerts, harvest_festivals, wine_harvest, oktoberfest, ice_hotels, snowy_landscapes

### infrastructure (select ONE):
developed, developing, remote, adventure_infrastructure

### tourism_characteristics (select ALL that apply):
beach_destination, ski_resort, cultural_hub, historical_city, party_destination, foodie_destination, shopping_destination, adventure_base, wellness_destination, business_hub, romantic_destination, family_destination, backpacker_friendly, luxury_destination, spiritual_center, art_capital, music_city, tech_hub, university_town

### special_features (select ALL that apply):
unesco_sites, theme_parks, casinos, cannabis_legal, lgbtq_friendly, nightlife_hub, wine_region, dive_sites, surf_spots, safari_access, ancient_ruins, royal_heritage, religious_significance, film_location, cruise_port, hot_springs

## INSTRUCTIONS

1. Research or use your knowledge about {city}, {country}
2. Select appropriate tags from EACH category above
3. Be accurate – only select tags that truly apply
4. Consider:
   - Physical geography (coastal? mountain? island?)
   - Climate and weather patterns
   - What the city is famous for tourism-wise
   - Seasonal events and features
   - Infrastructure level
   - Special attractions

## OUTPUT FORMAT

Return ONLY valid JSON, no other text:

{{
  "city": "{city}",
  "country": "{country}",
  "region": "<geo_region value>",
  "tags": {{
    "geo_type": ["<value1>", "<value2>"],
    "geo_region": ["<single value>"],
    "climate_type": ["<single value>"],
    "weather_characteristics": ["<value1>", "<value2>"],
    "seasonal_features": ["<value1>", "<value2>"],
    "infrastructure": ["<single value>"],
    "tourism_characteristics": ["<value1>", "<value2>"],
    "special_features": ["<value1>", "<value2>"]
  }},
  "confidence": "<high|medium|low>",
  "notes": "<brief note if low confidence>"
}}"""

        try:
            client = anthropic.Anthropic()
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract and parse JSON response
            response_text = response.content[0].text
            
            # Clean up markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            response_text = response_text.strip()
            
            # Parse JSON
            inferred_data = json.loads(response_text)
            
            # Add metadata
            inferred_data['from_database'] = False
            inferred_data['inference_confidence'] = inferred_data.get('confidence', 'medium')
            
            print(f"✓ AI inference complete (confidence: {inferred_data['inference_confidence']})")
            
            return inferred_data
            
        except Exception as e:
            print(f"❌ AI inference failed: {e}")
            # Return fallback generic city data
            return self._get_fallback_city_data(city, country)
    
    @staticmethod
    def _get_fallback_city_data(city: str, country: str) -> Dict[str, Any]:
        """Return generic fallback data when AI inference fails."""
        return {
            "city": city,
            "country": country,
            "region": "unknown",
            "tags": {
                "geo_type": ["urban"],
                "geo_region": ["unknown"],
                "climate_type": ["unknown"],
                "weather_characteristics": [],
                "seasonal_features": [],
                "infrastructure": ["developed"],
                "tourism_characteristics": ["cultural_hub"],
                "special_features": []
            },
            "from_database": False,
            "inference_confidence": "fallback",
            "notes": "Using generic fallback data due to inference failure"
        }


# ============================================================================
# PART 2: DATE AND SEASON HANDLING
# ============================================================================

def calculate_season(travel_date: date, hemisphere: str = "northern") -> str:
    """
    Calculate season based on date and hemisphere.
    
    Args:
        travel_date: Date of travel
        hemisphere: "northern" or "southern"
    
    Returns:
        str: Season name ("spring", "summer", "autumn", "winter")
    """
    month = travel_date.month
    
    # Northern hemisphere seasons
    if hemisphere == "northern":
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:  # 12, 1, 2
            return "winter"
    
    # Southern hemisphere seasons (reversed)
    else:
        if month in [3, 4, 5]:
            return "autumn"
        elif month in [6, 7, 8]:
            return "winter"
        elif month in [9, 10, 11]:
            return "spring"
        else:  # 12, 1, 2
            return "summer"


def get_hemisphere(geo_region: str) -> str:
    """Determine hemisphere from geo_region."""
    southern_regions = [
        "oceania", "pacific_islands",
        "south_america", "sub_saharan_africa"
    ]
    
    if geo_region in southern_regions:
        return "southern"
    return "northern"


def detect_special_periods(travel_date: date) -> List[str]:
    """Detect special time periods from travel date."""
    special_periods = []
    
    month = travel_date.month
    day = travel_date.day
    
    # Christmas period (Dec 1 - Jan 6)
    if (month == 12) or (month == 1 and day <= 6):
        special_periods.append("christmas_period")
    
    # Easter (approximate - late March to late April)
    if month == 3 and day >= 20:
        special_periods.append("easter")
    elif month == 4 and day <= 25:
        special_periods.append("easter")
    
    # Halloween
    if month == 10 and day >= 25:
        special_periods.append("halloween")
    
    # Summer holidays (June-August in Northern, Dec-Feb in Southern)
    if month in [6, 7, 8, 12, 1, 2]:
        special_periods.append("summer_holidays")
    
    return special_periods


def get_date_context(dates: Dict[str, str], city_tags: Dict) -> Dict[str, Any]:
    """
    Calculate comprehensive date context including season and special periods.
    
    Args:
        dates: Dict with "start" and "end" date strings (YYYY-MM-DD)
        city_tags: City tag dictionary with geo_region
    
    Returns:
        Dict with season info and special periods
    """
    start_date = datetime.strptime(dates['start'], '%Y-%m-%d').date()
    
    # Determine hemisphere
    geo_region = city_tags.get('geo_region', ['unknown'])[0]
    hemisphere = get_hemisphere(geo_region)
    
    # Calculate season
    season = calculate_season(start_date, hemisphere)
    
    # Detect special periods
    special_periods = detect_special_periods(start_date)
    
    # Check for seasonal features in city
    city_seasonal = city_tags.get('seasonal_features', [])
    relevant_seasonal = [s for s in special_periods if s in city_seasonal]
    
    return {
        "season": season,
        "adjusted_season": season,  # Could be modified for tropical regions
        "special_periods": relevant_seasonal,
        "hemisphere": hemisphere,
        "month": start_date.month
    }


# ============================================================================
# PART 3: FILTERING LOGIC
# ============================================================================

# Define neighboring regions for cuisine proximity scoring
NEIGHBOR_REGIONS = {
    "eastern_europe": ["western_europe", "northern_europe", "southern_europe", "central_asia", "middle_east"],
    "western_europe": ["eastern_europe", "northern_europe", "southern_europe", "north_africa"],
    "northern_europe": ["western_europe", "eastern_europe"],
    "southern_europe": ["western_europe", "eastern_europe", "north_africa", "middle_east"],
    "middle_east": ["eastern_europe", "southern_europe", "north_africa", "central_asia", "south_asia"],
    "central_asia": ["eastern_europe", "middle_east", "south_asia", "east_asia"],
    "east_asia": ["southeast_asia", "central_asia", "oceania"],
    "southeast_asia": ["east_asia", "south_asia", "oceania"],
    "south_asia": ["middle_east", "central_asia", "southeast_asia"],
    "north_africa": ["western_europe", "southern_europe", "middle_east", "sub_saharan_africa"],
    "sub_saharan_africa": ["north_africa", "middle_east"],
    "north_america": ["central_america", "caribbean"],
    "central_america": ["north_america", "south_america", "caribbean"],
    "south_america": ["central_america", "caribbean"],
    "caribbean": ["north_america", "central_america", "south_america"],
    "oceania": ["east_asia", "southeast_asia", "pacific_islands"],
    "pacific_islands": ["oceania", "southeast_asia"]
}


def check_hard_filters(category: Dict, user_input: Dict, city_tags: Dict,
                       date_context: Dict) -> Tuple[bool, Optional[str]]:
    """
    Apply hard exclusion filters. Returns (passes, reason_if_failed).
    
    Hard filters are absolute requirements that must be met.
    """
    cat_tags = category.get('tags', {})
    
    # 1. TRIP TYPE EXCLUSIONS
    trip_type = user_input.get('trip_type')
    if trip_type in cat_tags.get('trip_exclude', []):
        return False, f"trip_type '{trip_type}' is excluded"
    
    # 2. BUDGET EXCLUSIONS
    budget = user_input.get('budget')
    if budget in cat_tags.get('budget_exclude', []):
        return False, f"budget '{budget}' is excluded"
    
    # 3. GEO_TYPE REQUIREMENTS
    required_geo = cat_tags.get('geo_type', [])
    city_geo = city_tags.get('geo_type', [])
    
    if required_geo and required_geo != ['all'] and not any(g in city_geo for g in required_geo):
        return False, f"geo_type mismatch: requires {required_geo}, city has {city_geo}"
    
    # 4. GEO_REGION REQUIREMENTS
    required_regions = cat_tags.get('geo_region', [])
    city_region = city_tags.get('geo_region', [])
    
    if required_regions and 'all' not in required_regions:
        if not any(r in city_region for r in required_regions):
            return False, f"geo_region mismatch: requires {required_regions}, city has {city_region}"
    
    # 5. INFRASTRUCTURE REQUIREMENTS
    required_infra = cat_tags.get('infrastructure', [])
    city_infra = city_tags.get('infrastructure', [])
    
    if required_infra and required_infra != ['all']:
        if not any(i in city_infra for i in required_infra):
            return False, f"infrastructure mismatch: requires {required_infra}, city has {city_infra}"
    
    # 6. WEATHER REQUIREMENTS
    weather_req = cat_tags.get('weather_requirement', [])
    if 'warm_weather_required' in weather_req:
        if date_context['season'] == 'winter':
            city_climate = city_tags.get('climate_type', [])
            if not any(c in ['tropical', 'subtropical', 'mediterranean'] for c in city_climate):
                return False, "warm weather required but visiting in cold season"
    
    if 'cold_weather_required' in weather_req:
        if date_context['season'] in ['summer', 'spring']:
            return False, "cold weather required but visiting in warm season"
    
    # All filters passed
    return True, None


def calculate_relevance_score(category: Dict, user_input: Dict, city_tags: Dict,
                              date_context: Dict) -> int:
    """
    Calculate relevance score for a category (0-100).
    Higher score = more relevant to the user's trip.
    """
    score = 0
    cat_tags = category.get('tags', {})
    
    # BASE SCORES
    
    # 1. TRIP TYPE MATCH (+15 if ideal)
    trip_type = user_input.get('trip_type')
    if trip_type in cat_tags.get('trip_ideal', []):
        score += 15
    
    # 2. BUDGET MATCH (+10 if matches)
    budget = user_input.get('budget')
    if budget in cat_tags.get('budget_level', []):
        score += 10
    
    # 3. SEASON MATCH (+20 for perfect season, +10 for all-season)
    category_seasons = cat_tags.get('season', [])
    if date_context['season'] in category_seasons:
        score += 20
    elif 'all_season' in category_seasons:
        score += 10
    
    # 4. SPECIAL PERIOD BONUS (+15 if matches)
    season_special = cat_tags.get('season_special', [])
    for special in date_context.get('special_periods', []):
        if special in season_special:
            score += 15
            break
    
    # 5. TOURISM CHARACTERISTICS ALIGNMENT (+5 per match, max +20)
    cat_tourism_req = cat_tags.get('tourism_characteristics', [])
    city_tourism = city_tags.get('tourism_characteristics', [])
    tourism_matches = sum(1 for t in cat_tourism_req if t in city_tourism)
    score += min(tourism_matches * 5, 20)
    
    # 6. SPECIAL FEATURES MATCH (+10 per match, max +20)
    cat_special_req = cat_tags.get('special_features', [])
    city_special = city_tags.get('special_features', [])
    special_matches = sum(1 for s in cat_special_req if s in city_special)
    score += min(special_matches * 10, 20)
    
    # 7. VIBE BONUSES
    vibe_tags = cat_tags.get('vibe', [])
    if 'bucket_list' in vibe_tags:
        score += 5
    if 'instagram_worthy' in vibe_tags:
        score += 3

    # 8. CUISINE HOME_REGION BONUS (for dining categories)
    # This gives higher scores to cuisines that originate from or near the destination
    home_region = cat_tags.get('home_region')
    if home_region:
        city_region = city_tags.get('geo_region', [])
        city_region_str = city_region[0] if city_region else None

        if home_region == "global":
            # Global cuisines (Italian, Chinese, etc.) get bonus everywhere
            score += 10
        elif city_region_str:
            if home_region == city_region_str:
                # Cuisine is from this region (e.g., Bulgarian in Bulgaria)
                score += 20
            elif city_region_str in NEIGHBOR_REGIONS.get(home_region, []):
                # Cuisine is from neighboring region (e.g., Turkish in Bulgaria)
                score += 12
            elif home_region in NEIGHBOR_REGIONS.get(city_region_str, []):
                # Reverse check - city is neighbor of cuisine's home
                score += 12

    return min(score, 100)  # Cap at 100


# ============================================================================
# PART 4: MAIN FILTERING FUNCTION
# ============================================================================

def filter_categories(all_categories: List[Dict], city: str, country: str,
                     user_input: Dict, city_db: CityDatabase) -> Dict[str, Any]:
    """
    Main filtering function that orchestrates the entire process.
    
    Args:
        all_categories: List of all category dictionaries
        city: City name
        country: Country name
        user_input: User input dictionary with destination, dates, trip_type, budget
        city_db: CityDatabase instance
    
    Returns:
        Dict with filtered and scored categories, organized by type
    """
    
    # STEP 1: Get city data (from database or AI inference)
    city_data = city_db.get_city_data(city, country)
    city_tags = city_data.get('tags', {})
    
    # STEP 2: Calculate date context
    date_context = get_date_context(user_input['dates'], city_tags)
    
    # STEP 3: Filter and score categories
    results = {
        'places': [],
        'activities': [],
        'dining_cuisines': [],
        'dining_formats': [],
        'dining_dietary': []
    }
    
    excluded_categories = []
    
    for category in all_categories:
        list_type = category.get('list', 'unknown')
        
        # Apply hard filters
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        if not passes:
            excluded_categories.append({
                'name': category['name'],
                'parent': category.get('parent_category', ''),
                'reason': reason
            })
            continue
        
        # Calculate relevance score
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Add to results
        result_item = {
            'name': category['name'],
            'parent_category': category.get('parent_category', ''),
            'relevance_score': score,
            'search_query_template': category.get('search_query_template', ''),
            'description': category.get('description', '')
        }
        
        if list_type in results:
            results[list_type].append(result_item)
    
    # STEP 4: Sort by relevance score (highest first)
    for list_type in results:
        results[list_type].sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # STEP 5: Apply fallback if needed
    results = apply_fallback_if_empty(results, all_categories)
    
    # STEP 6: Compile final output
    output = {
        'city_info': {
            'city': city,
            'country': country,
            'from_database': city_data.get('from_database', False),
            'inference_confidence': city_data.get('inference_confidence'),
            'city_tags': {
                'geo_type': city_tags.get('geo_type', []),
                'geo_region': city_tags.get('geo_region', []),
                'climate_type': city_tags.get('climate_type', []),
                'tourism_characteristics': city_tags.get('tourism_characteristics', []),
                'special_features': city_tags.get('special_features', [])
            }
        },
        'date_context': date_context,
        'places': results['places'],
        'activities': results['activities'],
        'dining': {
            'cuisines': results['dining_cuisines'],
            'formats': results['dining_formats'],
            'dietary': results['dining_dietary']
        },
        'excluded_count': len(excluded_categories),
        'excluded_examples': excluded_categories[:5]  # Show first 5 examples
    }
    
    return output


def apply_fallback_if_empty(results: Dict, all_categories: List[Dict]) -> Dict:
    """If category lists are empty, return generic fallback options."""
    
    for list_type in ['places', 'activities']:
        if not results.get(list_type, []):
            # Find all-season, geo-agnostic categories
            generic = []
            for cat in all_categories:
                if cat.get('list') != list_type:
                    continue
                
                tags = cat.get('tags', {})
                # Must be all-season and not geo-specific
                if ('all_season' in tags.get('season', []) and 
                    (not tags.get('geo_type') or tags.get('geo_type') == ['all'])):
                    
                    generic.append({
                        'name': cat['name'],
                        'parent_category': cat.get('parent_category', ''),
                        'relevance_score': 0,
                        'search_query_template': cat.get('search_query_template', ''),
                        'is_fallback': True
                    })
            
            if generic:
                results[list_type] = generic[:10]
                print(f"⚠️  No {list_type} matched filters. Using {len(generic[:10])} generic fallbacks.")
    
    return results


# ============================================================================
# PART 5: CATEGORY LOADING UTILITY
# ============================================================================

def load_categories(categories_json_path: str) -> List[Dict]:
    """
    Load and flatten categories from JSON file into a list.
    
    Returns:
        List of category dictionaries with metadata
    """
    with open(categories_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = []
    
    # Load places
    for parent_name, parent_data in data.get('places', {}).items():
        for subcat in parent_data.get('subcategories', []):
            subcat['list'] = 'places'
            subcat['parent_category'] = parent_name
            categories.append(subcat)
    
    # Load activities
    for parent_name, parent_data in data.get('activities', {}).items():
        for subcat in parent_data.get('subcategories', []):
            subcat['list'] = 'activities'
            subcat['parent_category'] = parent_name
            categories.append(subcat)
    
    # Load dining - cuisines
    for cuisine_type, cuisine_data in data.get('dining', {}).get('cuisines', {}).items():
        for subcat in cuisine_data.get('subcategories', []):
            subcat['list'] = 'dining_cuisines'
            subcat['parent_category'] = cuisine_type
            categories.append(subcat)
    
    # Load dining - formats
    for subcat in data.get('dining', {}).get('formats', {}).get('subcategories', []):
        subcat['list'] = 'dining_formats'
        subcat['parent_category'] = 'Dining Formats'
        categories.append(subcat)
    
    # Load dining - dietary
    for subcat in data.get('dining', {}).get('dietary', {}).get('subcategories', []):
        subcat['list'] = 'dining_dietary'
        subcat['parent_category'] = 'Dietary Options'
        categories.append(subcat)
    
    print(f"Loaded {len(categories)} total categories")
    return categories
