import React, { useState } from 'react';
import { FilterResponse, CategoryItem } from '../types';

interface ResultsProps {
  data: FilterResponse;
}

// Group items by parent_category
const groupByParent = (items: CategoryItem[]): Map<string, CategoryItem[]> => {
  const grouped = new Map<string, CategoryItem[]>();
  items.forEach(item => {
    const parent = item.parent_category || 'Other';
    if (!grouped.has(parent)) {
      grouped.set(parent, []);
    }
    grouped.get(parent)!.push(item);
  });
  return grouped;
};

// Subcategory item component
const SubcategoryItem: React.FC<{ item: CategoryItem }> = ({ item }) => (
  <div className="subcategory-item">
    <span className="subcategory-name">{item.name}</span>
    <span className="relevance-score" title="Relevance Score">
      {item.relevance_score}
    </span>
    {item.is_fallback && <span className="fallback-badge">Fallback</span>}
  </div>
);

// Parent category accordion component
const ParentCategoryAccordion: React.FC<{
  parentName: string;
  items: CategoryItem[];
  defaultExpanded?: boolean;
}> = ({ parentName, items, defaultExpanded = false }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  // Calculate average score for parent
  const avgScore = Math.round(items.reduce((sum, item) => sum + item.relevance_score, 0) / items.length);

  return (
    <div className="parent-category-accordion">
      <div className="parent-header" onClick={() => setExpanded(!expanded)}>
        <div className="parent-title">
          <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
          <span className="parent-name">{parentName}</span>
          <span className="subcategory-count">({items.length})</span>
        </div>
        <span className="parent-avg-score" title="Average Relevance Score">
          avg: {avgScore}
        </span>
      </div>
      {expanded && (
        <div className="subcategories-list">
          {items.map((item, idx) => (
            <SubcategoryItem key={`${item.name}-${idx}`} item={item} />
          ))}
        </div>
      )}
    </div>
  );
};

// Main section component (Places, Activities, Cuisines)
const AccordionSection: React.FC<{
  title: string;
  items: CategoryItem[];
  defaultExpanded?: boolean;
}> = ({ title, items, defaultExpanded = true }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const grouped = groupByParent(items);

  if (items.length === 0) return null;

  return (
    <div className="accordion-section">
      <div className="section-header" onClick={() => setExpanded(!expanded)}>
        <h3>{title} ({items.length})</h3>
        <span className="expand-icon">{expanded ? '−' : '+'}</span>
      </div>
      {expanded && (
        <div className="parent-categories-list">
          {Array.from(grouped.entries()).map(([parentName, subcategories]) => (
            <ParentCategoryAccordion
              key={parentName}
              parentName={parentName}
              items={subcategories}
              defaultExpanded={grouped.size === 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const Results: React.FC<ResultsProps> = ({ data }) => {
  const { city_info, date_context, places, activities, dining, excluded_count } = data;

  return (
    <div className="results-container">
      <div className="trip-summary">
        <h2>Results for {city_info.city}, {city_info.country}</h2>

        <div className="info-cards">
          <div className="info-card">
            <h4>City Info</h4>
            <p><strong>Source:</strong> {city_info.from_database ? 'Database' : 'AI Inference'}</p>
            {city_info.inference_confidence && (
              <p><strong>Confidence:</strong> {city_info.inference_confidence}</p>
            )}
            <div className="tags">
              {city_info.city_tags.tourism_characteristics.slice(0, 5).map(tag => (
                <span key={tag} className="tag">{tag.replace(/_/g, ' ')}</span>
              ))}
            </div>
          </div>

          <div className="info-card">
            <h4>Travel Context</h4>
            <p><strong>Season:</strong> {date_context.season}</p>
            <p><strong>Hemisphere:</strong> {date_context.hemisphere}</p>
            {date_context.special_periods.length > 0 && (
              <p><strong>Special:</strong> {date_context.special_periods.join(', ')}</p>
            )}
          </div>

          <div className="info-card">
            <h4>Filtering Stats</h4>
            <p><strong>Places:</strong> {places.length} matches</p>
            <p><strong>Activities:</strong> {activities.length} matches</p>
            <p><strong>Dining:</strong> {dining.cuisines.length + dining.formats.length + dining.dietary.length} matches</p>
            <p><strong>Excluded:</strong> {excluded_count} categories</p>
          </div>
        </div>
      </div>

      <AccordionSection title="Places to Visit" items={places} />
      <AccordionSection title="Activities" items={activities} />
      <AccordionSection title="Cuisines" items={dining.cuisines} />
      <AccordionSection title="Dining Formats" items={dining.formats} defaultExpanded={false} />
      <AccordionSection title="Dietary Options" items={dining.dietary} defaultExpanded={false} />

      {data.excluded_examples && data.excluded_examples.length > 0 && (
        <div className="excluded-section">
          <h3>Sample Excluded Categories</h3>
          <div className="excluded-list">
            {data.excluded_examples.map((ex, idx) => (
              <div key={idx} className="excluded-item">
                <span className="excluded-name">{ex.name}</span>
                <span className="excluded-reason">{ex.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;
