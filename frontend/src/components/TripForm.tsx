import React, { useState, useEffect } from 'react';
import { CountryData, DateRange, TRIP_TYPES, BUDGET_OPTIONS } from '../types';

interface TripFormProps {
  onSubmit: (data: {
    city: string;
    country: string;
    dates: DateRange;
    trip_type: string;
    budget: string;
    limit: number;
  }) => void;
  loading: boolean;
}

const TripForm: React.FC<TripFormProps> = ({ onSubmit, loading }) => {
  const [countries, setCountries] = useState<CountryData[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [tripType, setTripType] = useState<string>('');
  const [budget, setBudget] = useState<string>('');
  const [limit, setLimit] = useState<number>(20);
  const [loadingCities, setLoadingCities] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchCities();
  }, []);

  const fetchCities = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/cities');
      if (!response.ok) throw new Error('Failed to fetch cities');
      const data = await response.json();
      setCountries(data);
    } catch (err) {
      setError('Failed to load cities. Make sure the backend is running.');
    } finally {
      setLoadingCities(false);
    }
  };

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCountry(e.target.value);
    setSelectedCity('');
  };

  const citiesForCountry = countries.find(c => c.country === selectedCountry)?.cities || [];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCountry || !selectedCity || !startDate || !endDate || !tripType || !budget) {
      setError('Please fill in all fields');
      return;
    }
    setError('');
    onSubmit({
      city: selectedCity,
      country: selectedCountry,
      dates: { start: startDate, end: endDate },
      trip_type: tripType,
      budget: budget,
      limit: limit
    });
  };

  const handleLimitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (value >= 10) {
      setLimit(value);
    } else if (e.target.value === '') {
      setLimit(10);
    }
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <form onSubmit={handleSubmit} className="trip-form">
      <h2>Plan Your Trip</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="country">Country</label>
        <select
          id="country"
          value={selectedCountry}
          onChange={handleCountryChange}
          disabled={loadingCities}
        >
          <option value="">Select a country...</option>
          {countries.map(c => (
            <option key={c.country} value={c.country}>{c.country}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="city">City</label>
        <select
          id="city"
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          disabled={!selectedCountry}
        >
          <option value="">Select a city...</option>
          {citiesForCountry.map(city => (
            <option key={city.city} value={city.city}>{city.city}</option>
          ))}
        </select>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="startDate">Start Date</label>
          <input
            type="date"
            id="startDate"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            min={today}
          />
        </div>

        <div className="form-group">
          <label htmlFor="endDate">End Date</label>
          <input
            type="date"
            id="endDate"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            min={startDate || today}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="tripType">What kind of trip are you planning?</label>
        <select
          id="tripType"
          value={tripType}
          onChange={(e) => setTripType(e.target.value)}
        >
          <option value="">Select trip type...</option>
          {TRIP_TYPES.map(type => (
            <option key={type.value} value={type.value}>{type.label}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="budget">What's your budget range?</label>
        <select
          id="budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
        >
          <option value="">Select budget...</option>
          {BUDGET_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="limit">Max categories per type (min 10)</label>
        <input
          type="number"
          id="limit"
          value={limit}
          onChange={handleLimitChange}
          min={10}
          placeholder="20"
        />
      </div>

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Loading...' : 'Get Recommendations'}
      </button>
    </form>
  );
};

export default TripForm;
