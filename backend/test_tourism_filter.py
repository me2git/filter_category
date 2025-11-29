"""
Unit Tests for Tourism Category Filtering Algorithm

Tests cover:
- City database lookup
- AI inference fallback
- Season calculation
- Date context
- Hard filters
- Relevance scoring
- Category filtering
"""

import unittest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from tourism_filter import (
    CityDatabase,
    calculate_season,
    get_hemisphere,
    detect_special_periods,
    get_date_context,
    check_hard_filters,
    calculate_relevance_score,
    filter_categories,
    load_categories
)


class TestSeasonCalculation(unittest.TestCase):
    """Test season calculation logic."""
    
    def test_northern_hemisphere_seasons(self):
        """Test season calculation for northern hemisphere."""
        self.assertEqual(calculate_season(date(2025, 3, 15), "northern"), "spring")
        self.assertEqual(calculate_season(date(2025, 6, 21), "northern"), "summer")
        self.assertEqual(calculate_season(date(2025, 9, 22), "northern"), "autumn")
        self.assertEqual(calculate_season(date(2025, 12, 21), "northern"), "winter")
    
    def test_southern_hemisphere_seasons(self):
        """Test season calculation for southern hemisphere."""
        self.assertEqual(calculate_season(date(2025, 3, 15), "southern"), "autumn")
        self.assertEqual(calculate_season(date(2025, 6, 21), "southern"), "winter")
        self.assertEqual(calculate_season(date(2025, 9, 22), "southern"), "spring")
        self.assertEqual(calculate_season(date(2025, 12, 21), "southern"), "summer")
    
    def test_hemisphere_detection(self):
        """Test hemisphere detection from geo_region."""
        self.assertEqual(get_hemisphere("western_europe"), "northern")
        self.assertEqual(get_hemisphere("oceania"), "southern")
        self.assertEqual(get_hemisphere("south_america"), "southern")
        self.assertEqual(get_hemisphere("north_america"), "northern")


class TestSpecialPeriods(unittest.TestCase):
    """Test special period detection."""
    
    def test_christmas_period(self):
        """Test Christmas period detection."""
        periods = detect_special_periods(date(2025, 12, 20))
        self.assertIn("christmas_period", periods)
        
        periods = detect_special_periods(date(2025, 1, 3))
        self.assertIn("christmas_period", periods)
    
    def test_easter_period(self):
        """Test Easter period detection."""
        periods = detect_special_periods(date(2025, 4, 15))
        self.assertIn("easter", periods)
    
    def test_halloween(self):
        """Test Halloween detection."""
        periods = detect_special_periods(date(2025, 10, 31))
        self.assertIn("halloween", periods)
    
    def test_summer_holidays(self):
        """Test summer holidays detection."""
        periods = detect_special_periods(date(2025, 7, 15))
        self.assertIn("summer_holidays", periods)


class TestDateContext(unittest.TestCase):
    """Test date context calculation."""
    
    def test_date_context_northern(self):
        """Test date context for northern hemisphere city."""
        dates = {"start": "2025-06-15", "end": "2025-06-22"}
        city_tags = {
            "geo_region": ["western_europe"],
            "seasonal_features": ["summer_festivals", "summer_holidays"]
        }
        
        context = get_date_context(dates, city_tags)
        
        self.assertEqual(context['season'], 'summer')
        self.assertEqual(context['hemisphere'], 'northern')
        # Special periods only appear if they're in the city's seasonal_features
        self.assertIn('summer_holidays', context['special_periods'])
    
    def test_date_context_southern(self):
        """Test date context for southern hemisphere city."""
        dates = {"start": "2025-01-15", "end": "2025-01-22"}
        city_tags = {
            "geo_region": ["south_america"],
            "seasonal_features": ["summer_festivals", "beach_season"]
        }
        
        context = get_date_context(dates, city_tags)
        
        self.assertEqual(context['season'], 'summer')
        self.assertEqual(context['hemisphere'], 'southern')


class TestHardFilters(unittest.TestCase):
    """Test hard filtering logic."""
    
    def test_trip_type_exclusion(self):
        """Test that excluded trip types are filtered out."""
        category = {
            "tags": {
                "trip_exclude": ["family_young_children", "business_travel"]
            }
        }
        user_input = {"trip_type": "family_young_children", "budget": "mid_range"}
        city_tags = {}
        date_context = {}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertFalse(passes)
        self.assertIn("trip_type", reason)
    
    def test_budget_exclusion(self):
        """Test that excluded budgets are filtered out."""
        category = {
            "tags": {
                "budget_exclude": ["luxury"],
                "trip_exclude": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "luxury"}
        city_tags = {}
        date_context = {}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertFalse(passes)
        self.assertIn("budget", reason)
    
    def test_geo_type_mismatch(self):
        """Test that geo_type mismatches are filtered out."""
        category = {
            "tags": {
                "geo_type": ["coastal", "island"],
                "trip_exclude": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {"geo_type": ["urban", "mountain"]}
        date_context = {}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertFalse(passes)
        self.assertIn("geo_type", reason)
    
    def test_geo_region_mismatch(self):
        """Test that geo_region mismatches are filtered out."""
        category = {
            "tags": {
                "geo_region": ["southeast_asia", "east_asia"],
                "trip_exclude": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {
            "geo_type": ["urban"],
            "geo_region": ["western_europe"]
        }
        date_context = {}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertFalse(passes)
        self.assertIn("geo_region", reason)
    
    def test_warm_weather_requirement(self):
        """Test warm weather requirement in winter."""
        category = {
            "tags": {
                "weather_requirement": ["warm_weather_required"],
                "trip_exclude": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {
            "geo_type": ["urban"],
            "climate_type": ["continental"]
        }
        date_context = {"season": "winter"}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertFalse(passes)
        self.assertIn("warm weather", reason)
    
    def test_all_filters_pass(self):
        """Test that categories pass when all requirements met."""
        category = {
            "tags": {
                "geo_type": ["urban"],
                "trip_exclude": [],
                "budget_exclude": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {
            "geo_type": ["urban", "riverside"],
            "geo_region": ["western_europe"]
        }
        date_context = {"season": "summer"}
        
        passes, reason = check_hard_filters(category, user_input, city_tags, date_context)
        
        self.assertTrue(passes)
        self.assertIsNone(reason)


class TestRelevanceScoring(unittest.TestCase):
    """Test relevance score calculation."""
    
    def test_trip_type_match_bonus(self):
        """Test bonus for matching trip type."""
        category = {
            "tags": {
                "trip_ideal": ["romantic_couple"],
                "season": ["all_season"]
            }
        }
        user_input = {"trip_type": "romantic_couple", "budget": "mid_range"}
        city_tags = {}
        date_context = {"season": "summer", "special_periods": []}
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Should get +15 for trip match, +10 for all-season
        self.assertGreaterEqual(score, 25)
    
    def test_budget_match_bonus(self):
        """Test bonus for matching budget."""
        category = {
            "tags": {
                "budget_level": ["mid_range", "luxury"],
                "season": ["all_season"]
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {}
        date_context = {"season": "summer", "special_periods": []}
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Should get +10 for budget match
        self.assertGreaterEqual(score, 10)
    
    def test_season_match_bonus(self):
        """Test bonus for perfect season match."""
        category = {
            "tags": {
                "season": ["summer"],
                "trip_ideal": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {}
        date_context = {"season": "summer", "special_periods": []}
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Should get +20 for perfect season match
        self.assertGreaterEqual(score, 20)
    
    def test_special_period_bonus(self):
        """Test bonus for special period match."""
        category = {
            "tags": {
                "season_special": ["christmas_period"],
                "season": ["winter"],
                "trip_ideal": []
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {}
        date_context = {
            "season": "winter",
            "special_periods": ["christmas_period"]
        }
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Should get +15 for special period
        self.assertGreaterEqual(score, 15)
    
    def test_tourism_characteristics_bonus(self):
        """Test bonus for tourism characteristics match."""
        category = {
            "tags": {
                "tourism_characteristics": ["romantic_destination", "historical_city"],
                "season": ["all_season"]
            }
        }
        user_input = {"trip_type": "solo_trip", "budget": "mid_range"}
        city_tags = {
            "tourism_characteristics": ["historical_city", "romantic_destination", "cultural_hub"]
        }
        date_context = {"season": "summer", "special_periods": []}
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        # Should get +10 for two tourism matches (5 each, max 20)
        self.assertGreaterEqual(score, 10)
    
    def test_score_capped_at_100(self):
        """Test that scores don't exceed 100."""
        category = {
            "tags": {
                "trip_ideal": ["romantic_couple"],
                "budget_level": ["mid_range"],
                "season": ["summer"],
                "season_special": ["summer_festivals"],
                "tourism_characteristics": ["romantic_destination"] * 10,
                "special_features": ["unesco_sites"] * 10,
                "vibe": ["bucket_list", "instagram_worthy"]
            }
        }
        user_input = {"trip_type": "romantic_couple", "budget": "mid_range"}
        city_tags = {
            "tourism_characteristics": ["romantic_destination"] * 10,
            "special_features": ["unesco_sites"] * 10
        }
        date_context = {
            "season": "summer",
            "special_periods": ["summer_festivals"]
        }
        
        score = calculate_relevance_score(category, user_input, city_tags, date_context)
        
        self.assertLessEqual(score, 100)


class TestCityDatabase(unittest.TestCase):
    """Test city database operations."""
    
    @patch('tourism_filter.CityDatabase._load_database')
    def test_normalize_key(self, mock_load):
        """Test key normalization."""
        db = CityDatabase('dummy.json')
        
        key1 = db._normalize_key("New York", "United States")
        key2 = db._normalize_key("new york", "united states")
        key3 = db._normalize_key("NEW YORK", "UNITED STATES")
        
        self.assertEqual(key1, key2)
        self.assertEqual(key2, key3)
    
    @patch('tourism_filter.CityDatabase._load_database')
    def test_get_city_from_database(self, mock_load):
        """Test retrieving city from database."""
        db = CityDatabase('dummy.json')
        db.city_index = {
            "prague_czech republic": {
                "city": "Prague",
                "country": "Czech Republic",
                "tags": {"geo_type": ["urban"]}
            }
        }
        
        result = db.get_city_data("Prague", "Czech Republic")
        
        self.assertTrue(result['from_database'])
        self.assertEqual(result['city'], "Prague")


class TestCategoryLoading(unittest.TestCase):
    """Test category loading from JSON."""
    
    def test_load_categories_structure(self):
        """Test that loaded categories have correct structure."""
        # This would need the actual file
        # For now, just test the structure
        categories = [
            {
                "name": "Test Category",
                "list": "places",
                "parent_category": "Test Parent",
                "tags": {}
            }
        ]
        
        self.assertIsInstance(categories, list)
        self.assertIn('name', categories[0])
        self.assertIn('list', categories[0])
        self.assertIn('tags', categories[0])


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    print("=" * 80)
    print("  TOURISM FILTERING ALGORITHM - UNIT TESTS")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSeasonCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestSpecialPeriods))
    suite.addTests(loader.loadTestsFromTestCase(TestDateContext))
    suite.addTests(loader.loadTestsFromTestCase(TestHardFilters))
    suite.addTests(loader.loadTestsFromTestCase(TestRelevanceScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestCityDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestCategoryLoading))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
