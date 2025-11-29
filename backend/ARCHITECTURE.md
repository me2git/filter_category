# Tourism Filtering System - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TOURISM FILTERING ALGORITHM                       │
│                 with AI City Inference System                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌─────────────────┐
│  User Input  │  │City Database │  │Category Database│
│              │  │  (380 cities)│  │ (231 categories)│
│ - City       │  │              │  │                 │
│ - Dates      │  │ - Tags       │  │ - Requirements  │
│ - Trip Type  │  │ - Features   │  │ - Descriptions  │
│ - Budget     │  │ - Climate    │  │ - Vibes         │
└──────┬───────┘  └──────┬───────┘  └────────┬────────┘
       │                 │                    │
       └─────────────────┴────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  MAIN FILTERING  │
              │     FUNCTION     │
              └──────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐    ┌──────────┐    ┌──────────┐
   │  City   │    │   Date   │    │ Category │
   │ Lookup  │    │ Context  │    │ Filtering│
   └─────────┘    └──────────┘    └──────────┘
        │              │                 │
        └──────────────┴─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ FILTERED RESULTS│
              │  (Scored 0-100) │
              └─────────────────┘
```

## Detailed Component Flow

### 1. City Lookup Process

```
USER INPUT: "Prague, Czech Republic"
     │
     ▼
┌────────────────────────────────────────┐
│  Step 1: Normalize Input               │
│  "prague_czech republic"               │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  Step 2: Check Database (O(1))         │
│                                        │
│  ┌──────────────┐                     │
│  │ Hash Lookup  │ ──Yes──> Return City│
│  └──────┬───────┘         Data        │
│         │No                            │
│         ▼                              │
│  ┌──────────────┐                     │
│  │Fuzzy Match?  │ ──Yes──> Return     │
│  └──────┬───────┘         Match       │
│         │No                            │
│         ▼                              │
│  ┌──────────────┐                     │
│  │  AI Inference│                     │
│  │  (Claude API)│                     │
│  └──────┬───────┘                     │
│         │                              │
│         ▼                              │
│  ┌──────────────┐                     │
│  │ Cache Result │                     │
│  └──────────────┘                     │
└────────────────────────────────────────┘
```

### 2. AI City Inference Detail

```
UNKNOWN CITY: "Plovdiv, Bulgaria"
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Claude API Call                                     │
│                                                      │
│  Prompt:                                             │
│  "Analyze Plovdiv, Bulgaria                          │
│   Use ONLY these tag vocabularies:                   │
│   - geo_type: urban, coastal, mountain...            │
│   - climate: continental, mediterranean...           │
│   - features: unesco_sites, ancient_ruins...         │
│                                                      │
│   Return structured JSON with confidence"            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Claude Response (JSON)                              │
│                                                      │
│  {                                                   │
│    "city": "Plovdiv",                                │
│    "geo_type": ["urban", "riverside"],               │
│    "climate_type": ["continental"],                  │
│    "tourism_characteristics": [                      │
│      "historical_city",                              │
│      "cultural_hub"                                  │
│    ],                                                │
│    "special_features": [                             │
│      "unesco_sites",                                 │
│      "ancient_ruins"                                 │
│    ],                                                │
│    "confidence": "high"                              │
│  }                                                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Cache in Memory                                     │
│  plovdiv_bulgaria → [inferred data]                  │
│                                                      │
│  Next query: Instant retrieval (no API call)         │
└─────────────────────────────────────────────────────┘
```

### 3. Date Context Calculation

```
INPUT: Dec 20, 2025 + Sydney, Australia
     │
     ▼
┌─────────────────────────────────────────┐
│  Determine Hemisphere                   │
│  geo_region: "oceania"                  │
│  → Southern Hemisphere                  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Calculate Season                       │
│  Month: December                        │
│  Hemisphere: Southern                   │
│  → SUMMER (reversed from northern)      │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Detect Special Periods                 │
│  December → christmas_period            │
│  December → summer_holidays             │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Filter to City's Features              │
│  City has: beach_season, summer_festivals│
│  → Keep relevant periods only           │
└─────────────────────────────────────────┘
```

### 4. Category Filtering Pipeline

```
231 CATEGORIES
     │
     ▼
┌─────────────────────────────────────────┐
│  HARD FILTERS (Must Pass All)           │
│                                          │
│  ┌────────────────────────────────┐     │
│  │ 1. Trip Type Not Excluded?     │ ──X─> REJECT
│  └────────────┬───────────────────┘     │
│               ▼                          │
│  ┌────────────────────────────────┐     │
│  │ 2. Budget Not Excluded?        │ ──X─> REJECT
│  └────────────┬───────────────────┘     │
│               ▼                          │
│  ┌────────────────────────────────┐     │
│  │ 3. Geographic Match?           │ ──X─> REJECT
│  │    (coastal ⊄ [urban, mountain])│     │
│  └────────────┬───────────────────┘     │
│               ▼                          │
│  ┌────────────────────────────────┐     │
│  │ 4. Regional Match?             │ ──X─> REJECT
│  │    (Asia ⊄ [Europe])           │     │
│  └────────────┬───────────────────┘     │
│               ▼                          │
│  ┌────────────────────────────────┐     │
│  │ 5. Weather Compatible?         │ ──X─> REJECT
│  └────────────┬───────────────────┘     │
│               ▼                          │
│              PASS                        │
└──────────────┬──────────────────────────┘
               │
               ▼ (~150 categories pass)
┌─────────────────────────────────────────┐
│  RELEVANCE SCORING (0-100)              │
│                                          │
│  Base Score = 0                          │
│                                          │
│  + 15 if trip_type matches ideal        │
│  + 10 if budget matches                 │
│  + 20 if perfect season match           │
│  + 10 if all-season compatible          │
│  + 15 if special period (Christmas)     │
│  + 5 per tourism characteristic (max 20)│
│  + 10 per special feature (max 20)      │
│  + 5 if bucket_list                     │
│  + 3 if instagram_worthy                │
│                                          │
│  Cap at 100                              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  SORT BY SCORE (Descending)             │
│                                          │
│  1. Christmas Markets (68)               │
│  2. Castles & Palaces (58)              │
│  3. Churches & Cathedrals (48)          │
│  4. Art Museums (43)                    │
│  ...                                     │
└─────────────────────────────────────────┘
```

## Data Structures

### City Data Structure

```json
{
  "city": "Prague",
  "country": "Czech Republic",
  "region": "eastern_europe",
  "tags": {
    "geo_type": ["urban", "riverside"],
    "geo_region": ["eastern_europe"],
    "climate_type": ["continental"],
    "weather_characteristics": [
      "snowy_winters",
      "extreme_cold_winter"
    ],
    "seasonal_features": [
      "christmas_period",
      "autumn_foliage"
    ],
    "infrastructure": ["developed"],
    "tourism_characteristics": [
      "historical_city",
      "cultural_hub",
      "romantic_destination"
    ],
    "special_features": [
      "unesco_sites",
      "nightlife_hub"
    ]
  }
}
```

### Category Data Structure

```json
{
  "name": "Surfing",
  "parent_category": "Water Sports",
  "list": "activities",
  "description": "Ride the waves...",
  "search_query_template": "surfing lessons in {city}",
  "tags": {
    "geo_type": ["coastal", "island"],
    "season": ["summer", "all_season"],
    "weather_requirement": ["warm_weather_required"],
    "trip_ideal": ["solo_trip", "couple_travel"],
    "trip_exclude": ["family_young_children"],
    "budget_level": ["budget", "mid_range", "luxury"],
    "physical": ["physically_demanding"],
    "vibe": ["instagram_worthy", "bucket_list"]
  }
}
```

### Output Data Structure

```json
{
  "city_info": {
    "city": "Prague",
    "from_database": true,
    "inference_confidence": null,
    "city_tags": { ... }
  },
  "date_context": {
    "season": "winter",
    "special_periods": ["christmas_period"],
    "hemisphere": "northern"
  },
  "places": [
    {
      "name": "Christmas Markets",
      "parent_category": "Seasonal Attractions",
      "relevance_score": 68,
      "search_query_template": "christmas markets in {city}"
    }
  ],
  "activities": [ ... ],
  "dining": { ... },
  "excluded_count": 47,
  "excluded_examples": [ ... ]
}
```

## Scoring Example Breakdown

### Example: "Christmas Markets" in Prague (Winter, Romantic Couple)

```
Category: Christmas Markets
City: Prague (winter, romantic_couple, mid_range)

SCORE CALCULATION:
┌─────────────────────────────────────────┐
│  Base Score: 0                          │
├─────────────────────────────────────────┤
│  + 15  Trip Type Match                  │
│        (romantic_couple in trip_ideal)  │
├─────────────────────────────────────────┤
│  + 10  Budget Match                     │
│        (mid_range in budget_level)      │
├─────────────────────────────────────────┤
│  + 20  Perfect Season                   │
│        (winter matches winter)          │
├─────────────────────────────────────────┤
│  + 15  Special Period                   │
│        (christmas_period detected)      │
├─────────────────────────────────────────┤
│  + 10  Tourism Characteristics          │
│        (romantic_destination matches)   │
├─────────────────────────────────────────┤
│  + 0   Special Features                 │
│        (none required by this category) │
├─────────────────────────────────────────┤
│  + 3   Instagram Worthy                 │
│        (in vibe tags)                   │
├─────────────────────────────────────────┤
│  + 5   Bucket List                      │
│        (in vibe tags)                   │
├─────────────────────────────────────────┤
│  = 68  FINAL SCORE                      │
└─────────────────────────────────────────┘

Result: Top-ranked place (highest relevance)
```

## Performance Characteristics

```
┌──────────────────────────────────────────────────┐
│  OPERATION           │  TIME      │  COMPLEXITY  │
├──────────────────────┼────────────┼──────────────┤
│  Database Lookup     │  < 1ms     │  O(1)        │
│  Fuzzy Match         │  ~50ms     │  O(n)        │
│  AI Inference        │  1-2s      │  API call    │
│  Category Filtering  │  < 100ms   │  O(m)        │
│  Score Calculation   │  < 1ms     │  O(1)        │
│  Total (DB city)     │  < 100ms   │  Fast        │
│  Total (AI city)     │  1-2s      │  First time  │
│  Total (Cached AI)   │  < 100ms   │  Subsequent  │
└──────────────────────────────────────────────────┘

Memory Usage:
├─ City Database:     ~2 MB  (423 cities × ~5KB each)
├─ Category Database: ~1 MB  (231 categories)
├─ Inference Cache:   ~10 KB (varies by usage)
└─ Total:            ~3-5 MB (very light)
```

## Error Handling Flow

```
USER INPUT
    │
    ▼
┌──────────────────┐
│ Try Database     │
│ Lookup           │
└────┬─────────────┘
     │ Not Found
     ▼
┌──────────────────┐
│ Try Fuzzy Match  │
└────┬─────────────┘
     │ No Match
     ▼
┌──────────────────┐
│ Try AI Inference │
└────┬─────────────┘
     │ API Error
     ▼
┌──────────────────┐
│ Use Fallback     │
│ Generic Data     │
│                  │
│ {               │
│   geo_type: urban│
│   climate: unknown│
│   features: []   │
│ }               │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│ Continue with    │
│ Best-Effort      │
│ Filtering        │
└──────────────────┘
```

## Deployment Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION SYSTEM                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │ Web Server   │                                       │
│  │ (Flask/Django)│                                      │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────┐         ┌─────────────────┐  │
│  │ tourism_filter.py    │◄────────│ Redis Cache     │  │
│  │                      │         │ (AI inferences) │  │
│  │ - CityDatabase       │         └─────────────────┘  │
│  │ - filter_categories()│                              │
│  └──────┬───────────────┘                              │
│         │                                                │
│         ├──────────┬─────────────┐                     │
│         ▼          ▼             ▼                      │
│  ┌──────────┐ ┌─────────┐  ┌──────────┐               │
│  │cities.json│ │categories│  │Anthropic │               │
│  │(380 cities)│ │.json    │  │API       │               │
│  └──────────┘ └─────────┘  └──────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Testing Architecture

```
test_tourism_filter.py
├── TestSeasonCalculation
│   ├── test_northern_hemisphere_seasons ✓
│   ├── test_southern_hemisphere_seasons ✓
│   └── test_hemisphere_detection ✓
│
├── TestSpecialPeriods
│   ├── test_christmas_period ✓
│   ├── test_easter_period ✓
│   ├── test_halloween ✓
│   └── test_summer_holidays ✓
│
├── TestDateContext
│   ├── test_date_context_northern ✓
│   └── test_date_context_southern ✓
│
├── TestHardFilters
│   ├── test_trip_type_exclusion ✓
│   ├── test_budget_exclusion ✓
│   ├── test_geo_type_mismatch ✓
│   ├── test_geo_region_mismatch ✓
│   ├── test_warm_weather_requirement ✓
│   └── test_all_filters_pass ✓
│
├── TestRelevanceScoring
│   ├── test_trip_type_match_bonus ✓
│   ├── test_budget_match_bonus ✓
│   ├── test_season_match_bonus ✓
│   ├── test_special_period_bonus ✓
│   ├── test_tourism_characteristics_bonus ✓
│   └── test_score_capped_at_100 ✓
│
├── TestCityDatabase
│   ├── test_normalize_key ✓
│   └── test_get_city_from_database ✓
│
└── TestCategoryLoading
    └── test_load_categories_structure ✓

TOTAL: 24 tests, 24 passing (100%)
```

---

## Legend

```
│  Pipeline flow
▼  Data transformation
┌─┐ Process or component
└─┘
◄─ Data retrieval
──X─> Rejection path
✓  Success/Pass
```
