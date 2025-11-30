import React, { useState, useEffect } from 'react';
import { AllCategories as AllCategoriesType, ParentCategory, Subcategory } from '../types';

interface AllCategoriesProps {
  apiUrl: string;
}

// Tag item component - displays a single tag
const TagBadge: React.FC<{ tag: string }> = ({ tag }) => (
  <span className="tag-badge">{tag.replace(/_/g, ' ')}</span>
);

// Tags group component - displays tags for a category
const TagsGroup: React.FC<{ label: string; tags: string[] }> = ({ label, tags }) => {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="tags-group">
      <span className="tags-label">{label}:</span>
      <div className="tags-list">
        {tags.map((tag, idx) => (
          <TagBadge key={`${tag}-${idx}`} tag={tag} />
        ))}
      </div>
    </div>
  );
};

// Subcategory item component with all details
const SubcategoryDetail: React.FC<{ item: Subcategory }> = ({ item }) => {
  const [expanded, setExpanded] = useState(false);

  // Get non-empty tag groups
  const tagGroups = Object.entries(item.tags || {})
    .filter(([_, values]) => values && values.length > 0)
    .map(([key, values]) => ({ label: key.replace(/_/g, ' '), tags: values as string[] }));

  return (
    <div className="subcategory-detail">
      <div className="subcategory-header" onClick={() => setExpanded(!expanded)}>
        <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
        <span className="subcategory-name">{item.name}</span>
      </div>
      <p className="subcategory-description">{item.description}</p>
      {expanded && (
        <div className="subcategory-tags">
          {tagGroups.map((group, idx) => (
            <TagsGroup key={idx} label={group.label} tags={group.tags} />
          ))}
        </div>
      )}
    </div>
  );
};

// Parent category accordion
const ParentCategorySection: React.FC<{
  name: string;
  category: ParentCategory;
}> = ({ name, category }) => {
  const [expanded, setExpanded] = useState(false);
  const subcategories = category?.subcategories || [];

  return (
    <div className="parent-category-section">
      <div className="parent-header" onClick={() => setExpanded(!expanded)}>
        <div className="parent-title">
          <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
          <span className="parent-name">{name}</span>
          <span className="subcategory-count">({subcategories.length})</span>
        </div>
      </div>
      {expanded && (
        <>
          <p className="parent-description">{category?.description}</p>
          <div className="subcategories-list">
            {subcategories.map((sub, idx) => (
              <SubcategoryDetail key={`${sub.name}-${idx}`} item={sub} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

// Single category section (for formats/dietary which have subcategories directly)
const SingleCategorySection: React.FC<{
  title: string;
  category: ParentCategory;
}> = ({ title, category }) => {
  const [expanded, setExpanded] = useState(true);
  const subcategories = category?.subcategories || [];

  if (subcategories.length === 0) return null;

  return (
    <div className="accordion-section">
      <div className="section-header" onClick={() => setExpanded(!expanded)}>
        <h3>{title} ({subcategories.length} subcategories)</h3>
        <span className="expand-icon">{expanded ? '−' : '+'}</span>
      </div>
      {expanded && (
        <div className="parent-categories-list">
          <div className="parent-category-section">
            <p className="parent-description">{category?.description}</p>
            <div className="subcategories-list">
              {subcategories.map((sub, idx) => (
                <SubcategoryDetail key={`${sub.name}-${idx}`} item={sub} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main section (Places, Activities, Dining types)
const CategorySection: React.FC<{
  title: string;
  categories: Record<string, ParentCategory>;
}> = ({ title, categories }) => {
  const [expanded, setExpanded] = useState(true);
  const entries = Object.entries(categories || {});

  if (entries.length === 0) return null;

  const totalSubcategories = entries.reduce(
    (sum, [_, cat]) => sum + (cat.subcategories?.length || 0),
    0
  );

  return (
    <div className="accordion-section">
      <div className="section-header" onClick={() => setExpanded(!expanded)}>
        <h3>{title} ({entries.length} categories, {totalSubcategories} subcategories)</h3>
        <span className="expand-icon">{expanded ? '−' : '+'}</span>
      </div>
      {expanded && (
        <div className="parent-categories-list">
          {entries.map(([name, category]) => (
            <ParentCategorySection key={name} name={name} category={category} />
          ))}
        </div>
      )}
    </div>
  );
};

const AllCategories: React.FC<AllCategoriesProps> = ({ apiUrl }) => {
  const [categories, setCategories] = useState<AllCategoriesType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const fetchCategories = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await fetch(`${apiUrl}/api/categories`);
        if (!response.ok) throw new Error('Failed to fetch categories');
        const data = await response.json();
        if (isMounted) {
          setCategories(data);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'An error occurred');
          setLoading(false);
        }
      }
    };

    fetchCategories();

    return () => {
      isMounted = false;
    };
  }, [apiUrl]);

  if (loading) {
    return <div className="loading-spinner">Loading all categories...</div>;
  }

  if (error) {
    return <div className="error-banner">{error}</div>;
  }

  if (!categories) {
    return <div className="placeholder">No categories available</div>;
  }

  return (
    <div className="all-categories-container">
      <div className="categories-summary">
        <h2>All Categories</h2>
        <p>Browse the complete category database used for filtering recommendations.</p>
      </div>

      <CategorySection title="Places" categories={categories.places} />
      <CategorySection title="Activities" categories={categories.activities} />
      {categories.dining && (
        <>
          <CategorySection title="Cuisines" categories={categories.dining.cuisines} />
          <SingleCategorySection title="Dining Formats" category={categories.dining.formats} />
          <SingleCategorySection title="Dietary Options" category={categories.dining.dietary} />
        </>
      )}
    </div>
  );
};

export default AllCategories;
