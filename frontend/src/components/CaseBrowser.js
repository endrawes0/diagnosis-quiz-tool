import React, { useState, useEffect, useCallback } from 'react';
import CaseCard from './CaseCard';
import FilterPanel from './FilterPanel';
import SearchBar from './SearchBar';
import Pagination from './Pagination';
import CaseDetail from './CaseDetail';
import CaseStudy from './CaseStudy';
import { casesAPI } from '../services/api';
import styles from '../styles/CaseBrowser.module.css';

const CaseBrowser = ({ userId, onExit }) => {
  const [cases, setCases] = useState([]);
  const [filteredCases, setFilteredCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [studyMode, setStudyMode] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    hasMore: false
  });
  const [filters, setFilters] = useState({
    category: '',
    age_group: '',
    complexity: '',
    diagnosis: '',
    sort: 'case_id',
    order: 'asc'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [categories, setCategories] = useState([]);
  const [ageGroups, setAgeGroups] = useState([]);
  const [complexityLevels, setComplexityLevels] = useState([]);
  const [userProgress, setUserProgress] = useState({});

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadCases();
  }, [filters, searchQuery, pagination.page]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [categoriesRes, ageGroupsRes, complexityRes] = await Promise.all([
        casesAPI.getCategories(),
        casesAPI.getAgeGroups(),
        casesAPI.getComplexityLevels()
      ]);

      setCategories(categoriesRes.data.categories || []);
      setAgeGroups(ageGroupsRes.data.age_groups || []);
      setComplexityLevels(complexityRes.data.complexity_levels || []);
    } catch (err) {
      setError('Failed to load initial data');
      console.error('Load initial data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        ...filters,
        limit: pagination.limit,
        offset: (pagination.page - 1) * pagination.limit
      };

      let response;
      if (searchQuery) {
        response = await casesAPI.searchCases({
          q: searchQuery,
          ...params
        });
      } else {
        response = await casesAPI.getCases(params);
      }

      const { cases: newCases, total_count, pagination: paginationInfo } = response.data;
      
      setCases(newCases);
      setFilteredCases(newCases);
      setPagination(prev => ({
        ...prev,
        total: total_count,
        hasMore: paginationInfo?.has_more || false
      }));

    } catch (err) {
      setError('Failed to load cases');
      console.error('Load cases error:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery, pagination.page, pagination.limit]);

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleCaseSelect = (caseItem) => {
    setSelectedCase(caseItem);
  };

  const handleCaseClose = () => {
    setSelectedCase(null);
  };

  const handleStudyMode = (caseItem) => {
    setSelectedCase(caseItem);
    setStudyMode(true);
  };

  const handleStudyModeClose = () => {
    setStudyMode(false);
    setSelectedCase(null);
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const handleSortChange = (sortField) => {
    const newOrder = filters.sort === sortField && filters.order === 'asc' ? 'desc' : 'asc';
    handleFilterChange({ sort: sortField, order: newOrder });
  };

  const getComplexityColor = (complexity) => {
    const colors = {
      basic: '#4CAF50',
      intermediate: '#FF9800',
      advanced: '#F44336',
      expert: '#9C27B0'
    };
    return colors[complexity] || '#757575';
  };

  const getAgeGroupIcon = (ageGroup) => {
    const icons = {
      child: '👶',
      adolescent: '🧑',
      adult: '👨',
      older_adult: '👴'
    };
    return icons[ageGroup] || '👤';
  };

  if (selectedCase && !studyMode) {
    return (
      <CaseDetail
        case={selectedCase}
        onClose={handleCaseClose}
        onStudyMode={() => handleStudyMode(selectedCase)}
        userId={userId}
      />
    );
  }

  if (selectedCase && studyMode) {
    return (
      <CaseStudy
        case={selectedCase}
        onClose={handleStudyModeClose}
        userId={userId}
      />
    );
  }

  return (
    <div className={styles.caseBrowser}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Case Browser</h1>
          <p className={styles.subtitle}>Explore and study diagnosis cases</p>
        </div>
        <div className={styles.headerActions}>
          <button
            onClick={onExit}
            className={styles.exitButton}
          >
            Exit Browser
          </button>
        </div>
      </div>

      <div className={styles.controls}>
        <SearchBar
          onSearch={handleSearch}
          placeholder="Search cases by diagnosis, symptoms, or keywords..."
          className={styles.searchBar}
        />
        
        <div className={styles.viewControls}>
          <button
            onClick={() => setViewMode('grid')}
            className={`${styles.viewButton} ${viewMode === 'grid' ? styles.active : ''}`}
            title="Grid View"
          >
            ⊞
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`${styles.viewButton} ${viewMode === 'list' ? styles.active : ''}`}
            title="List View"
          >
            ☰
          </button>
        </div>
      </div>

      <div className={styles.mainContent}>
        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          categories={categories}
          ageGroups={ageGroups}
          complexityLevels={complexityLevels}
          onSortChange={handleSortChange}
          className={styles.filterPanel}
        />

        <div className={styles.contentArea}>
          {error && (
            <div className={styles.error}>
              {error}
              <button onClick={loadCases} className={styles.retryButton}>
                Retry
              </button>
            </div>
          )}

          {loading ? (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Loading cases...</p>
            </div>
          ) : (
            <>
              <div className={styles.resultsHeader}>
                <span className={styles.resultsCount}>
                  {pagination.total} cases found
                </span>
                {searchQuery && (
                  <span className={styles.searchInfo}>
                    for "{searchQuery}"
                  </span>
                )}
              </div>

              {filteredCases.length === 0 ? (
                <div className={styles.noResults}>
                  <h3>No cases found</h3>
                  <p>Try adjusting your filters or search query</p>
                </div>
              ) : (
                <>
                  <div className={`${styles.casesContainer} ${styles[viewMode]}`}>
                    {filteredCases.map((caseItem) => (
                      <CaseCard
                        key={caseItem.case_id}
                        case={caseItem}
                        onSelect={() => handleCaseSelect(caseItem)}
                        onStudyMode={() => handleStudyMode(caseItem)}
                        viewMode={viewMode}
                        getComplexityColor={getComplexityColor}
                        getAgeGroupIcon={getAgeGroupIcon}
                        userProgress={userProgress[caseItem.case_id]}
                      />
                    ))}
                  </div>

                   {pagination.total > pagination.limit && (
                     <Pagination
                       currentPage={pagination.page}
                       totalPages={Math.ceil(pagination.total / pagination.limit)}
                       totalItems={pagination.total}
                       itemsPerPage={pagination.limit}
                       onPageChange={handlePageChange}
                     />
                   )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseBrowser;