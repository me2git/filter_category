"""
Example Usage: Tourism Category Filtering with AI City Inference

This script demonstrates how to use the filtering algorithm with:
1. Known cities (from database)
2. Unknown cities (using AI inference)
"""

import json
import os
from tourism_filter import (
    CityDatabase,
    filter_categories,
    load_categories
)


def print_results(results: dict, title: str):
    """Pretty print filtering results."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    
    # City info
    city_info = results['city_info']
    print(f"\n📍 CITY: {city_info['city']}, {city_info['country']}")
    print(f"   Source: {'Database' if city_info['from_database'] else 'AI Inference'}")
    if city_info['inference_confidence']:
        print(f"   Confidence: {city_info['inference_confidence']}")
    
    print(f"\n   Tags:")
    for tag_type, tag_values in city_info['city_tags'].items():
        if tag_values:
            print(f"   - {tag_type}: {', '.join(tag_values)}")
    
    # Date context
    date_ctx = results['date_context']
    print(f"\n📅 DATE CONTEXT:")
    print(f"   Season: {date_ctx['season']} ({date_ctx['hemisphere']} hemisphere)")
    if date_ctx['special_periods']:
        print(f"   Special periods: {', '.join(date_ctx['special_periods'])}")
    
    # Top results
    print(f"\n🏛️  TOP 10 PLACES:")
    for i, place in enumerate(results['places'][:25], 1):
        fallback = " [FALLBACK]" if place.get('is_fallback') else ""
        print(f"   {i:2d}. {place['name']:40s} (Score: {place['relevance_score']:3d}){fallback}")
        print(f"       └─ {place['parent_category']}")
    
    print(f"\n🎯 TOP 10 ACTIVITIES:")
    for i, activity in enumerate(results['activities'][:25], 1):
        fallback = " [FALLBACK]" if activity.get('is_fallback') else ""
        print(f"   {i:2d}. {activity['name']:40s} (Score: {activity['relevance_score']:3d}){fallback}")
        print(f"       └─ {activity['parent_category']}")
    
    print(f"\n🍽️  TOP 5 DINING OPTIONS:")
    dining = results['dining']
    if dining['cuisines']:
        print("   Cuisines:")
        for cuisine in dining['cuisines']:#[:3]:
            print(f"   - {cuisine['name']} (Score: {cuisine['relevance_score']})")
    if dining['formats']:
        print("   Formats:")
        for fmt in dining['formats']:#[:3]:
            print(f"   - {fmt['name']} (Score: {fmt['relevance_score']})")
    
    # Exclusions
    print(f"\n❌ EXCLUDED: {results['excluded_count']} categories filtered out")
    if results['excluded_examples']:
        print("   Examples:")
        for ex in results['excluded_examples'][:10]:
            print(f"   - {ex['name']} ({ex['parent']}): {ex['reason']}")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Run example scenarios."""
    
    # Check if API key is set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set. AI inference will fail.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'\n")
    
    # Load data
    print("Loading databases...")
    city_db = CityDatabase('cities.json')
    categories = load_categories('categories.json')
    print(f"Loaded {len(categories)} categories\n")
    
    # ========================================================================
    # EXAMPLE 1: Known City - Prague (Winter, Romantic)
    # ========================================================================
    
    print("\n🔍 EXAMPLE 1: Known City (Prague)")
    print("-" * 80)
    
    user_input_prague = {
        "destination": {
            "city": "Prague",
            "country": "Czech Republic"
        },
        "dates": {
            "start": "2025-12-18",
            "end": "2025-12-25"
        },
        "trip_type": "romantic_couple",
        "budget": "mid_range"
    }
    
    results_prague = filter_categories(
        categories,
        user_input_prague["destination"]["city"],
        user_input_prague["destination"]["country"],
        user_input_prague,
        city_db
    )
    
    print_results(results_prague, "PRAGUE - Winter Romantic Getaway")
    
    
    # ========================================================================
    # EXAMPLE 2: Known City - Tokyo (Spring, Family)
    # ========================================================================
    
    print("\n🔍 EXAMPLE 2: Known City (Tokyo)")
    print("-" * 80)
    
    user_input_tokyo = {
        "destination": {
            "city": "Tokyo",
            "country": "Japan"
        },
        "dates": {
            "start": "2025-04-01",
            "end": "2025-04-08"
        },
        "trip_type": "family_young_children",
        "budget": "mid_range"
    }
    
    results_tokyo = filter_categories(
        categories,
        user_input_tokyo["destination"]["city"],
        user_input_tokyo["destination"]["country"],
        user_input_tokyo,
        city_db
    )
    
    print_results(results_tokyo, "TOKYO - Spring Family Trip")
    
    
    # ========================================================================
    # EXAMPLE 3: Unknown City - Plovdiv, Bulgaria (AI Inference)
    # ========================================================================
    
    print("\n🔍 EXAMPLE 3: Unknown City (Plovdiv) - Will use AI Inference")
    print("-" * 80)
    
    user_input_plovdiv = {
        "destination": {
            "city": "Plovdiv",
            "country": "Bulgaria"
        },
        "dates": {
            "start": "2025-06-10",
            "end": "2025-06-17"
        },
        "trip_type": "couple_travel",
        "budget": "budget"
    }
    
    results_plovdiv = filter_categories(
        categories,
        user_input_plovdiv["destination"]["city"],
        user_input_plovdiv["destination"]["country"],
        user_input_plovdiv,
        city_db
    )
    
    print_results(results_plovdiv, "PLOVDIV - Summer Budget Trip (AI Inferred)")
    
    
    # ========================================================================
    # EXAMPLE 4: Another Unknown City - Valparaiso, Chile
    # ========================================================================
    
    print("\n🔍 EXAMPLE 4: Unknown City (Valparaiso) - Will use AI Inference")
    print("-" * 80)
    
    user_input_valpo = {
        "destination": {
            "city": "Valparaiso",
            "country": "Chile"
        },
        "dates": {
            "start": "2025-01-15",
            "end": "2025-01-22"
        },
        "trip_type": "solo_trip",
        "budget": "budget"
    }
    
    results_valpo = filter_categories(
        categories,
        user_input_valpo["destination"]["city"],
        user_input_valpo["destination"]["country"],
        user_input_valpo,
        city_db
    )
    
    print_results(results_valpo, "VALPARAISO - Summer Solo Trip (AI Inferred)")
    
    
    
    
    # ========================================================================
    # EXAMPLE 5: Known City - Ubud, Indonesia
    # ========================================================================
    
    print("\n🔍 EXAMPLE 5: Known City (Bali)")
    print("-" * 80)
    
    user_input_bali = {
        "destination": {
            "city": "Bali",
            "country": "Indonesia"
        },
        "dates": {
            "start": "2025-06-01",
            "end": "2025-06-10"
        },
        "trip_type": "solo_trip",
        "budget": "budget"
    }
    
    results_bali = filter_categories(
        categories,
        user_input_bali["destination"]["city"],
        user_input_bali["destination"]["country"],
        user_input_bali,
        city_db
    )
    
    print_results(results_bali, "BALI - Summer Solo Trip (budget)")


    # ========================================================================
    # EXAMPLE 6: Known City - Baku, Azerbaijan (Romantic Winter)
    # ========================================================================

    print("\n🔍 EXAMPLE 6: Known City (Baku)")
    print("-" * 80)

    user_input_baku = {
        "destination": {
            "city": "Baku",
            "country": "Azerbaijan"
        },
        "dates": {
            "start": "2026-10-15",
            "end": "2026-10-20"
        },
        "trip_type": "romantic_couple",
        "budget": "mid_range"
    }

    results_baku = filter_categories(
        categories,
        user_input_baku["destination"]["city"],
        user_input_baku["destination"]["country"],
        user_input_baku,
        city_db
    )

    print_results(results_baku, "BAKU - Winter Romantic Couple Trip")


    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    print("\nThe filtering algorithm successfully:")
    print("✓ Retrieved city data from database for known cities (Prague, Tokyo)")
    print("✓ Used AI inference for unknown cities (Plovdiv, Valparaiso)")
    print("✓ Adjusted seasons based on hemisphere")
    print("✓ Filtered categories based on hard requirements")
    print("✓ Scored and ranked categories by relevance")
    print("✓ Provided confidence levels for AI-inferred cities")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
