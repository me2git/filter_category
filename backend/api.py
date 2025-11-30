"""
Flask API for Tourism Category Filtering
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path

from tourism_filter import CityDatabase, filter_categories, load_categories

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize data on startup
BASE_DIR = Path(__file__).parent
CITIES_PATH = BASE_DIR / "cities.json"
CATEGORIES_PATH = BASE_DIR / "categories.json"

# Load data
city_db = CityDatabase(str(CITIES_PATH))
all_categories = load_categories(str(CATEGORIES_PATH))

# Load cities for dropdown
with open(CITIES_PATH, 'r', encoding='utf-8') as f:
    cities_data = json.load(f)


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all cities grouped by country for dropdowns."""
    countries = {}
    for city in cities_data.get('cities', []):
        country = city['country']
        if country not in countries:
            countries[country] = []
        countries[country].append({
            'city': city['city'],
            'region': city.get('region', '')
        })

    # Sort countries and cities
    result = []
    for country in sorted(countries.keys()):
        result.append({
            'country': country,
            'cities': sorted(countries[country], key=lambda x: x['city'])
        })

    return jsonify(result)


@app.route('/api/filter', methods=['POST'])
def filter_tourism_categories():
    """
    Filter categories based on user input.

    Expected JSON body:
    {
        "city": "Paris",
        "country": "France",
        "dates": {
            "start": "2024-06-15",
            "end": "2024-06-22"
        },
        "trip_type": "romantic_couple",
        "budget": "mid-range",
        "limit": 20
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['city', 'country', 'dates', 'trip_type', 'budget']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if 'start' not in data['dates'] or 'end' not in data['dates']:
            return jsonify({'error': 'Dates must include start and end'}), 400

        # Get limit parameter (default 20, minimum 10)
        limit = max(data.get('limit', 20), 10)

        # Prepare user input
        user_input = {
            'dates': data['dates'],
            'trip_type': data['trip_type'],
            'budget': data['budget']
        }

        # Filter categories
        result = filter_categories(
            all_categories=all_categories,
            city=data['city'],
            country=data['country'],
            user_input=user_input,
            city_db=city_db
        )

        # Apply limit to parent categories (not subcategories)
        # Group by parent_category, limit parents, then flatten back
        def limit_by_parent_category(items, max_parents):
            """Limit number of parent categories while keeping all their subcategories."""
            if not items:
                return items

            # Group items by parent_category
            parents = {}
            for item in items:
                parent = item.get('parent_category', 'Other')
                if parent not in parents:
                    parents[parent] = []
                parents[parent].append(item)

            # Calculate average score per parent for sorting
            parent_scores = {}
            for parent, subcats in parents.items():
                avg_score = sum(s['relevance_score'] for s in subcats) / len(subcats)
                parent_scores[parent] = avg_score

            # Sort parents by average score and take top N
            sorted_parents = sorted(parent_scores.keys(), key=lambda p: parent_scores[p], reverse=True)
            top_parents = sorted_parents[:max_parents]

            # Flatten back: return all subcategories from top parents
            result_items = []
            for parent in top_parents:
                result_items.extend(parents[parent])

            return result_items

        result['places'] = limit_by_parent_category(result['places'], limit)
        result['activities'] = limit_by_parent_category(result['activities'], limit)
        result['dining']['cuisines'] = limit_by_parent_category(result['dining']['cuisines'], limit)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    """Get all categories with their full structure."""
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        raw_categories = json.load(f)
    return jsonify(raw_categories)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'cities_loaded': len(cities_data.get('cities', [])),
        'categories_loaded': len(all_categories)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
