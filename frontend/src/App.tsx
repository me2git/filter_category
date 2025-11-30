import React, { useState } from 'react';
import './App.css';
import TripForm from './components/TripForm';
import Results from './components/Results';
import AllCategories from './components/AllCategories';
import { FilterResponse, DateRange } from './types';

type ViewMode = 'filter' | 'all-categories';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<FilterResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('filter');

  const handleSubmit = async (data: {
    city: string;
    country: string;
    dates: DateRange;
    trip_type: string;
    budget: string;
    limit: number;
  }) => {
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch(`${apiUrl}/api/filter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to filter categories');
      }

      const result = await response.json();
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Tourism Category Filter Test</h1>
        <p>Test the backend filtering API with different trip parameters</p>
        <div className="view-switch">
          <button
            className={`switch-btn ${viewMode === 'filter' ? 'active' : ''}`}
            onClick={() => setViewMode('filter')}
          >
            Filter Categories
          </button>
          <button
            className={`switch-btn ${viewMode === 'all-categories' ? 'active' : ''}`}
            onClick={() => setViewMode('all-categories')}
          >
            All Categories
          </button>
        </div>
      </header>

      <main className="App-main">
        {viewMode === 'filter' ? (
          <div className="content-wrapper">
            <div className="form-section">
              <TripForm onSubmit={handleSubmit} loading={loading} />
            </div>

            <div className="results-section">
              {error && <div className="error-banner">{error}</div>}
              {loading && <div className="loading-spinner">Loading recommendations...</div>}
              {results && <Results data={results} />}
              {!results && !loading && !error && (
                <div className="placeholder">
                  <p>Fill out the form and click "Get Recommendations" to see filtered categories.</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="all-categories-wrapper">
            <AllCategories apiUrl={apiUrl} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
