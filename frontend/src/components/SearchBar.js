import React, { useState, useEffect, useRef } from 'react';
import styles from '../styles/SearchBar.module.css';

const SearchBar = ({ onSearch, placeholder, className }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const inputRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.length > 2) {
      debounceRef.current = setTimeout(() => {
        fetchSuggestions(query);
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query]);

  const fetchSuggestions = async (searchQuery) => {
    try {
      // This would typically call an API endpoint for suggestions
      // For now, we'll use some common medical terms
      const commonTerms = [
        'depression', 'anxiety', 'bipolar disorder', 'schizophrenia',
        'ADHD', 'autism', 'PTSD', 'OCD', 'eating disorder',
        'substance abuse', 'dementia', 'Alzheimer', 'Parkinson',
        'headache', 'migraine', 'seizure', 'stroke', 'TIA',
        'chest pain', 'shortness of breath', 'cough', 'fever',
        'abdominal pain', 'nausea', 'vomiting', 'diarrhea'
      ];

      const filtered = commonTerms.filter(term =>
        term.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 8);

      setSuggestions(filtered);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    performSearch(query);
  };

  const performSearch = (searchQuery) => {
    if (searchQuery.trim()) {
      setIsSearching(true);
      
      // Add to search history
      const newHistory = [searchQuery, ...searchHistory.filter(h => h !== searchQuery)].slice(0, 10);
      setSearchHistory(newHistory);
      localStorage.setItem('searchHistory', JSON.stringify(newHistory));
      
      onSearch(searchQuery);
      setShowSuggestions(false);
      
      setTimeout(() => {
        setIsSearching(false);
      }, 1000);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    performSearch(suggestion);
    inputRef.current?.focus();
  };

  const handleHistoryClick = (historyItem) => {
    setQuery(historyItem);
    performSearch(historyItem);
  };

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    onSearch('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      // Focus first suggestion
      const firstSuggestion = document.querySelector(`.${styles.suggestionItem}`);
      if (firstSuggestion) {
        firstSuggestion.focus();
      }
    }
  };

  const getSearchIcon = () => {
    if (isSearching) {
      return (
        <div className={styles.searchSpinner}>
          <div className={styles.spinner}></div>
        </div>
      );
    }
    return (
      <svg className={styles.searchIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
    );
  };

  return (
    <div className={`${styles.searchBar} ${className || ''}`}>
      <form onSubmit={handleSubmit} className={styles.searchForm}>
        <div className={styles.searchInputContainer}>
          <div className={styles.searchIconContainer}>
            {getSearchIcon()}
          </div>
          
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || "Search cases..."}
            className={styles.searchInput}
            autoComplete="off"
          />
          
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className={styles.clearButton}
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>

        <button
          type="submit"
          className={styles.searchButton}
          disabled={!query.trim() || isSearching}
        >
          Search
        </button>
      </form>

      {showSuggestions && (suggestions.length > 0 || searchHistory.length > 0) && (
        <div className={styles.suggestionsContainer}>
          {suggestions.length > 0 && (
            <div className={styles.suggestionsSection}>
              <div className={styles.suggestionsHeader}>Suggestions</div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className={styles.suggestionItem}
                  onClick={() => handleSuggestionClick(suggestion)}
                  type="button"
                >
                  <svg className={styles.suggestionIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                  </svg>
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {searchHistory.length > 0 && (
            <div className={styles.suggestionsSection}>
              <div className={styles.suggestionsHeader}>Recent Searches</div>
              {searchHistory.slice(0, 5).map((historyItem, index) => (
                <button
                  key={index}
                  className={`${styles.suggestionItem} ${styles.historyItem}`}
                  onClick={() => handleHistoryClick(historyItem)}
                  type="button"
                >
                  <svg className={styles.historyIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                  {historyItem}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {query && !showSuggestions && (
        <div className={styles.searchTips}>
          <div className={styles.tip}>
            <strong>Tip:</strong> Use quotes for exact phrases, or try different keywords
          </div>
          <div className={styles.tip}>
            <strong>Examples:</strong> "chest pain", pediatric, depression, emergency
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;