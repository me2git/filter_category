"""
Simple Demo: Tourism Filtering (No API Key Required)

This demo uses only cities from the database, so no API key is needed.
It demonstrates the core filtering and scoring functionality.
"""

import json
from tourism_filter import (
    CityDatabase,
    filter_categories,
    load_categories
)


def simple_demo():
    """Run a simple demo with known cities only."""
    
    print("=" * 80)
    print("  TOURISM CATEGORY FILTERING - SIMPLE DEMO")
    print("  (Using database cities only - no API key required)")
    print("=" * 80)
    print()
    
    # Load data
    print("Loading databases...")
    city_db = CityDatabase('cities.json')
    categories = load_categories('categories.json')
    print(f"✓ Loaded {len(categories)} categories")
    print()
    
    # ========================================================================
    # Scenario 1: Prague in Winter (Christmas)
    # ========================================================================
    
    print("=" * 80)
    print("SCENARIO 1: Romantic Christmas in Prague")
    print("=" * 80)
    print()
    
    user_input = {
        "destination": {"city": "Prague", "country": "Czech Republic"},
        "dates": {"start": "2025-12-20", "end": "2025-12-27"},
        "trip_type": "romantic_couple",
        "budget": "mid_range"
    }
    
    print(f"📍 Destination: {user_input['destination']['city']}, {user_input['destination']['country']}")
    print(f"📅 Dates: {user_input['dates']['start']} to {user_input['dates']['end']}")
    print(f"👥 Trip Type: {user_input['trip_type']}")
    print(f"💰 Budget: {user_input['budget']}")
    print()
    
    results = filter_categories(
        categories,
        user_input["destination"]["city"],
        user_input["destination"]["country"],
        user_input,
        city_db
    )
    
    print(f"✓ City found in database: {results['city_info']['from_database']}")
    print(f"✓ Season: {results['date_context']['season']}")
    print(f"✓ Special periods: {', '.join(results['date_context']['special_periods']) or 'None'}")
    print()
    
    print("🏛️  TOP 10 PLACES TO VISIT:")
    for i, place in enumerate(results['places'][:10], 1):
        print(f"  {i:2d}. {place['name']:45s} Score: {place['relevance_score']:3d}/100")
    print()
    
    print("🎯 TOP 10 ACTIVITIES:")
    for i, activity in enumerate(results['activities'][:10], 1):
        print(f"  {i:2d}. {activity['name']:45s} Score: {activity['relevance_score']:3d}/100")
    print()
    
    # ========================================================================
    # Scenario 2: Bali in Summer (Beach vacation)
    # ========================================================================
    
    print("=" * 80)
    print("SCENARIO 2: Family Beach Holiday in Bali")
    print("=" * 80)
    print()
    
    user_input = {
        "destination": {"city": "Bali", "country": "Indonesia"},
        "dates": {"start": "2025-07-15", "end": "2025-07-29"},
        "trip_type": "family_young_children",
        "budget": "mid_range"
    }
    
    print(f"📍 Destination: {user_input['destination']['city']}, {user_input['destination']['country']}")
    print(f"📅 Dates: {user_input['dates']['start']} to {user_input['dates']['end']}")
    print(f"👥 Trip Type: {user_input['trip_type']}")
    print(f"💰 Budget: {user_input['budget']}")
    print()
    
    results = filter_categories(
        categories,
        user_input["destination"]["city"],
        user_input["destination"]["country"],
        user_input,
        city_db
    )
    
    print(f"✓ City found in database: {results['city_info']['from_database']}")
    print(f"✓ Season: {results['date_context']['season']}")
    print(f"✓ City characteristics: {', '.join(results['city_info']['city_tags']['tourism_characteristics'][:3])}")
    print()
    
    print("🏛️  TOP 10 PLACES TO VISIT:")
    for i, place in enumerate(results['places'][:10], 1):
        print(f"  {i:2d}. {place['name']:45s} Score: {place['relevance_score']:3d}/100")
    print()
    
    print("🎯 TOP 10 ACTIVITIES:")
    for i, activity in enumerate(results['activities'][:10], 1):
        print(f"  {i:2d}. {activity['name']:45s} Score: {activity['relevance_score']:3d}/100")
    print()
    
    # ========================================================================
    # Scenario 3: New York in Autumn (Solo Budget Trip)
    # ========================================================================
    
    print("=" * 80)
    print("SCENARIO 3: Solo Budget Adventure in New York")
    print("=" * 80)
    print()
    
    user_input = {
        "destination": {"city": "New York City", "country": "United States"},
        "dates": {"start": "2025-10-01", "end": "2025-10-07"},
        "trip_type": "solo_trip",
        "budget": "budget"
    }
    
    print(f"📍 Destination: {user_input['destination']['city']}, {user_input['destination']['country']}")
    print(f"📅 Dates: {user_input['dates']['start']} to {user_input['dates']['end']}")
    print(f"👥 Trip Type: {user_input['trip_type']}")
    print(f"💰 Budget: {user_input['budget']}")
    print()
    
    results = filter_categories(
        categories,
        user_input["destination"]["city"],
        user_input["destination"]["country"],
        user_input,
        city_db
    )
    
    print(f"✓ City found in database: {results['city_info']['from_database']}")
    print(f"✓ Season: {results['date_context']['season']}")
    print()
    
    print("🏛️  TOP 10 PLACES TO VISIT:")
    for i, place in enumerate(results['places'][:10], 1):
        print(f"  {i:2d}. {place['name']:45s} Score: {place['relevance_score']:3d}/100")
    print()
    
    print("🎯 TOP 10 ACTIVITIES:")
    for i, activity in enumerate(results['activities'][:10], 1):
        print(f"  {i:2d}. {activity['name']:45s} Score: {activity['relevance_score']:3d}/100")
    print()
    
    print("=" * 80)
    print()
    print("✨ Demo Complete!")
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Database city lookup (fast O(1) lookup)")
    print("  ✓ Hemisphere-aware season detection")
    print("  ✓ Special period identification (Christmas, summer holidays)")
    print("  ✓ Hard filtering (geographic, trip type, budget)")
    print("  ✓ Intelligent relevance scoring (0-100)")
    print("  ✓ Category ranking by relevance")
    print()
    print("To test AI city inference for unknown cities:")
    print("  1. Set ANTHROPIC_API_KEY environment variable")
    print("  2. Run: python example_usage.py")
    print()
    print("=" * 80)


if __name__ == "__main__":
    simple_demo()
