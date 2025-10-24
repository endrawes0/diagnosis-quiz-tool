import React, { useState } from 'react';
import styles from '../styles/FilterPanel.module.css';

const FilterPanel = ({ 
  filters, 
  onFilterChange, 
  categories, 
  ageGroups, 
  complexityLevels,
  onSortChange 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeSection, setActiveSection] = useState('filters');

  const handleFilterReset = () => {
    onFilterChange({
      category: '',
      age_group: '',
      complexity: '',
      diagnosis: '',
      sort: 'case_id',
      order: 'asc'
    });
  };

  const getActiveFiltersCount = () => {
    return Object.keys(filters).filter(key => 
      filters[key] && filters[key] !== '' && key !== 'sort' && key !== 'order'
    ).length;
  };

  const handleSortClick = (field) => {
    onSortChange(field);
  };

  const getSortIcon = (field) => {
    if (filters.sort !== field) return '↕';
    return filters.order === 'asc' ? '↑' : '↓';
  };

  return (
    <div className={`${styles.filterPanel} ${isExpanded ? styles.expanded : styles.collapsed}`}>
      <div className={styles.panelHeader}>
        <h3 className={styles.panelTitle}>
          Filters & Sort
          {getActiveFiltersCount() > 0 && (
            <span className={styles.activeFilterCount}>
              {getActiveFiltersCount()}
            </span>
          )}
        </h3>
        <button
          className={styles.toggleButton}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '◀' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className={styles.panelContent}>
          <div className={styles.sectionTabs}>
            <button
              className={`${styles.tabButton} ${activeSection === 'filters' ? styles.active : ''}`}
              onClick={() => setActiveSection('filters')}
            >
              Filters
            </button>
            <button
              className={`${styles.tabButton} ${activeSection === 'sort' ? styles.active : ''}`}
              onClick={() => setActiveSection('sort')}
            >
              Sort
            </button>
          </div>

          {activeSection === 'filters' && (
            <div className={styles.filtersSection}>
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Category</label>
                <select
                  value={filters.category || ''}
                  onChange={(e) => onFilterChange({ category: e.target.value })}
                  className={styles.filterSelect}
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.name} value={category.name}>
                      {category.display_name} ({category.case_count})
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Age Group</label>
                <select
                  value={filters.age_group || ''}
                  onChange={(e) => onFilterChange({ age_group: e.target.value })}
                  className={styles.filterSelect}
                >
                  <option value="">All Age Groups</option>
                  {ageGroups.map((ageGroup) => (
                    <option key={ageGroup.name} value={ageGroup.name}>
                      {ageGroup.display_name} ({ageGroup.case_count})
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Complexity</label>
                <select
                  value={filters.complexity || ''}
                  onChange={(e) => onFilterChange({ complexity: e.target.value })}
                  className={styles.filterSelect}
                >
                  <option value="">All Levels</option>
                  {complexityLevels.map((level) => (
                    <option key={level.name} value={level.name}>
                      {level.display_name} ({level.case_count})
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Diagnosis</label>
                <input
                  type="text"
                  value={filters.diagnosis || ''}
                  onChange={(e) => onFilterChange({ diagnosis: e.target.value })}
                  placeholder="Filter by diagnosis..."
                  className={styles.filterInput}
                />
              </div>

              <div className={styles.filterActions}>
                <button
                  onClick={handleFilterReset}
                  className={styles.resetButton}
                  disabled={getActiveFiltersCount() === 0}
                >
                  Reset Filters
                </button>
              </div>
            </div>
          )}

          {activeSection === 'sort' && (
            <div className={styles.sortSection}>
              <div className={styles.sortGroup}>
                <label className={styles.sortLabel}>Sort By</label>
                <div className={styles.sortOptions}>
                  <button
                    className={`${styles.sortButton} ${filters.sort === 'case_id' ? styles.active : ''}`}
                    onClick={() => handleSortClick('case_id')}
                  >
                    Case ID {getSortIcon('case_id')}
                  </button>
                  <button
                    className={`${styles.sortButton} ${filters.sort === 'difficulty' ? styles.active : ''}`}
                    onClick={() => handleSortClick('difficulty')}
                  >
                    Difficulty {getSortIcon('difficulty')}
                  </button>
                  <button
                    className={`${styles.sortButton} ${filters.sort === 'category' ? styles.active : ''}`}
                    onClick={() => handleSortClick('category')}
                  >
                    Category {getSortIcon('category')}
                  </button>
                  <button
                    className={`${styles.sortButton} ${filters.sort === 'age_group' ? styles.active : ''}`}
                    onClick={() => handleSortClick('age_group')}
                  >
                    Age Group {getSortIcon('age_group')}
                  </button>
                  <button
                    className={`${styles.sortButton} ${filters.sort === 'diagnosis' ? styles.active : ''}`}
                    onClick={() => handleSortClick('diagnosis')}
                  >
                    Diagnosis {getSortIcon('diagnosis')}
                  </button>
                </div>
              </div>

              <div className={styles.sortGroup}>
                <label className={styles.sortLabel}>Quick Filters</label>
                <div className={styles.quickFilters}>
                  <button
                    className={styles.quickFilterButton}
                    onClick={() => onFilterChange({ complexity: 'basic' })}
                  >
                    Beginner Friendly
                  </button>
                  <button
                    className={styles.quickFilterButton}
                    onClick={() => onFilterChange({ complexity: 'advanced,expert' })}
                  >
                    Challenging
                  </button>
                  <button
                    className={styles.quickFilterButton}
                    onClick={() => onFilterChange({ age_group: 'child,adolescent' })}
                  >
                    Pediatric
                  </button>
                  <button
                    className={styles.quickFilterButton}
                    onClick={() => onFilterChange({ age_group: 'adult,older_adult' })}
                  >
                    Adult
                  </button>
                </div>
              </div>
            </div>
          )}

          {getActiveFiltersCount() > 0 && (
            <div className={styles.activeFilters}>
              <h4 className={styles.activeFiltersTitle}>Active Filters:</h4>
              <div className={styles.activeFilterTags}>
                {filters.category && (
                  <span className={styles.filterTag}>
                    Category: {filters.category}
                    <button
                      onClick={() => onFilterChange({ category: '' })}
                      className={styles.removeFilter}
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.age_group && (
                  <span className={styles.filterTag}>
                    Age: {filters.age_group.replace('_', ' ')}
                    <button
                      onClick={() => onFilterChange({ age_group: '' })}
                      className={styles.removeFilter}
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.complexity && (
                  <span className={styles.filterTag}>
                    Level: {filters.complexity.replace('_', ' ')}
                    <button
                      onClick={() => onFilterChange({ complexity: '' })}
                      className={styles.removeFilter}
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.diagnosis && (
                  <span className={styles.filterTag}>
                    Diagnosis: {filters.diagnosis}
                    <button
                      onClick={() => onFilterChange({ diagnosis: '' })}
                      className={styles.removeFilter}
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FilterPanel;