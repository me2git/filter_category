export interface City {
  city: string;
  region: string;
}

export interface CountryData {
  country: string;
  cities: City[];
}

export interface DateRange {
  start: string;
  end: string;
}

export interface FilterRequest {
  city: string;
  country: string;
  dates: DateRange;
  trip_type: string;
  budget: string;
}

export interface CategoryItem {
  name: string;
  parent_category: string;
  relevance_score: number;
  search_query_template: string;
  description?: string;
  is_fallback?: boolean;
}

export interface CityInfo {
  city: string;
  country: string;
  from_database: boolean;
  inference_confidence: string | null;
  city_tags: {
    geo_type: string[];
    geo_region: string[];
    climate_type: string[];
    tourism_characteristics: string[];
    special_features: string[];
  };
}

export interface DateContext {
  season: string;
  adjusted_season: string;
  special_periods: string[];
  hemisphere: string;
  month: number;
}

export interface DiningResults {
  cuisines: CategoryItem[];
  formats: CategoryItem[];
  dietary: CategoryItem[];
}

export interface FilterResponse {
  city_info: CityInfo;
  date_context: DateContext;
  places: CategoryItem[];
  activities: CategoryItem[];
  dining: DiningResults;
  excluded_count: number;
  excluded_examples: Array<{
    name: string;
    parent: string;
    reason: string;
  }>;
}

export const TRIP_TYPES = [
  { label: "Solo trip", value: "solo_trip" },
  { label: "Romantic couple (honeymoon, anniversary)", value: "romantic_couple" },
  { label: "Couple travel (friends, non-romantic)", value: "couple_travel" },
  { label: "Family with young children (under 12)", value: "family_young_children" },
  { label: "Family with teenagers (13+)", value: "family_teens" },
  { label: "Group of friends", value: "group_friends" },
  { label: "Business travel", value: "business_travel" },
];

export const BUDGET_OPTIONS = [
  { label: "Budget-conscious ($)", value: "budget" },
  { label: "Mid-range ($$)", value: "mid-range" },
  { label: "Luxury ($$$)", value: "luxury" },
];
