import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import QuizPlayer from './components/QuizPlayer';
import CaseBrowser from './components/CaseBrowser';

import { authAPI, userAPI, casesAPI } from './services/api';
import styles from './styles/QuizPlayer.module.css';

const AppContent = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [quizConfig, setQuizConfig] = useState(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const [showCaseBrowser, setShowCaseBrowser] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await userAPI.getProfile();
        setUser(response.data);
      } catch (err) {
        localStorage.removeItem('token');
      }
    }
  };

  const handleLogin = async (credentials) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authAPI.login(credentials);
      localStorage.setItem('token', response.data.access_token);
      const userResponse = await userAPI.getProfile();
      setUser(userResponse.data);
    } catch (err) {
      setError('Login failed. Please check your credentials.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('token');
      setUser(null);
      setQuizConfig(null);
      setShowQuiz(false);
    }
  };

  const startQuiz = (config) => {
    setQuizConfig(config);
    setShowQuiz(true);
    navigate('/quiz');
  };

  const handleQuizComplete = (results) => {
    console.log('Quiz completed:', results);
    setShowQuiz(false);
    setQuizConfig(null);
  };

  const handleQuizExit = () => {
    setShowQuiz(false);
    setQuizConfig(null);
  };

  const openCaseBrowser = () => {
    setShowCaseBrowser(true);
  };

  const closeCaseBrowser = () => {
    setShowCaseBrowser(false);
  };

  const QuizConfigForm = () => {
    const [categories, setCategories] = useState([]);
    const [ageGroups, setAgeGroups] = useState([]);
    const [loadingFilters, setLoadingFilters] = useState(false);

    const [config, setConfig] = useState({
      difficulty: 'medium',
      categories: [], // Changed from category: 'all'
      age_groups: [], // New
      num_questions: 10,
      time_per_question: 60,
      adaptive_mode: false,
      multi_case_matching: false,
      untimed_mode: false
    });

    useEffect(() => {
      const loadFilters = async () => {
        setLoadingFilters(true);
        try {
          const [categoriesRes, ageGroupsRes] = await Promise.all([
            casesAPI.getCategories(),
            casesAPI.getAgeGroups()
          ]);

          setCategories(categoriesRes.data.categories || []);
          setAgeGroups(ageGroupsRes.data.age_groups || []);
        } catch (err) {
          console.error('Failed to load filters:', err);
          // Fallback to hardcoded values if API fails
          setCategories([
            {name: 'Neurodevelopmental Disorders', display_name: 'Neurodevelopmental Disorders', case_count: 0},
            {name: 'Schizophrenia Spectrum and Other Psychotic Disorders', display_name: 'Schizophrenia Spectrum and Other Psychotic Disorders', case_count: 0},
            {name: 'Bipolar and Related Disorders', display_name: 'Bipolar and Related Disorders', case_count: 0},
            {name: 'Depressive Disorders', display_name: 'Depressive Disorders', case_count: 0},
            {name: 'Anxiety Disorders', display_name: 'Anxiety Disorders', case_count: 0},
            {name: 'Obsessive-Compulsive and Related Disorders', display_name: 'Obsessive-Compulsive and Related Disorders', case_count: 0},
            {name: 'Trauma- and Stressor-Related Disorders', display_name: 'Trauma- and Stressor-Related Disorders', case_count: 0},
            {name: 'Dissociative Disorders', display_name: 'Dissociative Disorders', case_count: 0},
            {name: 'Somatic Symptom and Related Disorders', display_name: 'Somatic Symptom and Related Disorders', case_count: 0},
            {name: 'Feeding and Eating Disorders', display_name: 'Feeding and Eating Disorders', case_count: 0},
            {name: 'Elimination Disorders', display_name: 'Elimination Disorders', case_count: 0},
            {name: 'Sleep-Wake Disorders', display_name: 'Sleep-Wake Disorders', case_count: 0},
            {name: 'Sexual Dysfunctions', display_name: 'Sexual Dysfunctions', case_count: 0},
            {name: 'Gender Dysphoria', display_name: 'Gender Dysphoria', case_count: 0},
            {name: 'Disruptive, Impulse-Control, and Conduct Disorders', display_name: 'Disruptive, Impulse-Control, and Conduct Disorders', case_count: 0},
            {name: 'Substance-Related and Addictive Disorders', display_name: 'Substance-Related and Addictive Disorders', case_count: 0},
            {name: 'Neurocognitive Disorders', display_name: 'Neurocognitive Disorders', case_count: 0},
            {name: 'Personality Disorders', display_name: 'Personality Disorders', case_count: 0},
            {name: 'Paraphilic Disorders', display_name: 'Paraphilic Disorders', case_count: 0}
          ]);
          setAgeGroups([
            {name: 'child', display_name: 'Child', case_count: 0},
            {name: 'adolescent', display_name: 'Adolescent', case_count: 0},
            {name: 'adult', display_name: 'Adult', case_count: 0},
            {name: 'older_adult', display_name: 'Older Adult', case_count: 0}
          ]);
        } finally {
          setLoadingFilters(false);
        }
      };
      loadFilters();
    }, []);

    const handleMultiSelectChange = (field, value, checked) => {
      setConfig(prev => ({
        ...prev,
        [field]: checked
          ? [...prev[field], value]
          : prev[field].filter(item => item !== value)
      }));
    };

    const handleSelectAll = (field, options) => {
      setConfig(prev => ({
        ...prev,
        [field]: options.map(option => option.name)
      }));
    };

    const handleClearAll = (field) => {
      setConfig(prev => ({
        ...prev,
        [field]: []
      }));
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      console.log('Form submitted with config:', config);
      startQuiz(config);
    };

    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Diagnosis Quiz Tool</h1>
           <p className={styles.subtitle}>Test your diagnosis skills</p>
            <div className={styles.navigation}>
              <Link to="/cases" className={styles.navLink}>
                Browse Cases
              </Link>
            </div>
        </div>

        <div className={styles.quizContainer}>
          <div className={styles.questionContainer}>
            <h2>Quiz Configuration</h2>
            
            {error && (
              <div className={styles.error}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className={styles.quizForm}>
              {/* Basic Settings Section */}
              <div className={styles.formSection}>
                <h3 className={styles.sectionTitle}>Basic Settings</h3>

                <div className={styles.formGroup}>
                  <label htmlFor="num_questions">Number of Questions:</label>
                  <input
                    id="num_questions"
                    type="number"
                    min="1"
                    max="50"
                    value={config.num_questions}
                    onChange={(e) => setConfig({...config, num_questions: parseInt(e.target.value)})}
                    className={styles.formControl}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor="difficulty">Difficulty Level:</label>
                  <select
                    id="difficulty"
                    value={config.difficulty}
                    onChange={(e) => setConfig({...config, difficulty: e.target.value})}
                    className={styles.formControl}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                    <option value="mixed">Mixed</option>
                  </select>
                </div>
              </div>

              {/* Content Filters Section */}
              <div className={styles.formSection}>
                <h3 className={styles.sectionTitle}>Content Filters</h3>

                <div className={styles.formGroup}>
                  <label className={styles.groupLabel}>
                    Categories:
                    <div className={styles.selectActions}>
                      <button
                        type="button"
                        onClick={() => handleSelectAll('categories', categories)}
                        className={styles.actionButton}
                        disabled={loadingFilters}
                      >
                        Select All
                      </button>
                      <button
                        type="button"
                        onClick={() => handleClearAll('categories')}
                        className={styles.actionButton}
                        disabled={loadingFilters}
                      >
                        Clear All
                      </button>
                    </div>
                  </label>
                  <div className={styles.checkboxGrid}>
                    {loadingFilters ? (
                      <div className={styles.loading}>Loading categories...</div>
                    ) : (
                      categories.map(category => (
                        <label key={category.name} className={styles.checkboxLabel}>
                          <input
                            type="checkbox"
                            checked={config.categories.includes(category.name)}
                            onChange={(e) => handleMultiSelectChange('categories', category.name, e.target.checked)}
                            className={styles.checkbox}
                          />
                          {category.display_name} ({category.case_count})
                        </label>
                      ))
                    )}
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.groupLabel}>
                    Age Groups:
                    <div className={styles.selectActions}>
                      <button
                        type="button"
                        onClick={() => handleSelectAll('age_groups', ageGroups)}
                        className={styles.actionButton}
                        disabled={loadingFilters}
                      >
                        Select All
                      </button>
                      <button
                        type="button"
                        onClick={() => handleClearAll('age_groups')}
                        className={styles.actionButton}
                        disabled={loadingFilters}
                      >
                        Clear All
                      </button>
                    </div>
                  </label>
                  <div className={styles.checkboxGroup}>
                    {loadingFilters ? (
                      <div className={styles.loading}>Loading age groups...</div>
                    ) : (
                      ageGroups.map(ageGroup => (
                        <label key={ageGroup.name} className={styles.checkboxLabel}>
                          <input
                            type="checkbox"
                            checked={config.age_groups.includes(ageGroup.name)}
                            onChange={(e) => handleMultiSelectChange('age_groups', ageGroup.name, e.target.checked)}
                            className={styles.checkbox}
                          />
                          {ageGroup.display_name} ({ageGroup.case_count})
                        </label>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Quiz Settings Section */}
              <div className={styles.formSection}>
                <h3 className={styles.sectionTitle}>Quiz Settings</h3>

                 <div className={styles.formGroup}>
                   <label htmlFor="time_per_question">Time per Question (seconds):</label>
                   <input
                     id="time_per_question"
                     type="number"
                     min="10"
                     max="300"
                     value={config.time_per_question}
                     onChange={(e) => setConfig({...config, time_per_question: parseInt(e.target.value)})}
                     className={styles.formControl}
                     disabled={config.untimed_mode}
                   />
                 </div>

                 <div className={styles.formGroup}>
                   <label className={styles.checkboxLabel}>
                     <input
                       type="checkbox"
                       checked={config.untimed_mode}
                       onChange={(e) => setConfig({...config, untimed_mode: e.target.checked})}
                       className={styles.checkbox}
                     />
                     Untimed Mode (no time limits per question)
                   </label>
                 </div>

                 <div className={styles.formGroup}>
                   <label className={styles.checkboxLabel}>
                     <input
                       type="checkbox"
                       checked={config.adaptive_mode}
                       onChange={(e) => setConfig({...config, adaptive_mode: e.target.checked})}
                       className={styles.checkbox}
                     />
                     Adaptive Mode (difficulty adjusts based on performance)
                   </label>
                 </div>

                 <div className={styles.formGroup}>
                   <label className={styles.checkboxLabel}>
                     <input
                       type="checkbox"
                       checked={config.multi_case_matching}
                       onChange={(e) => setConfig({...config, multi_case_matching: e.target.checked})}
                       className={styles.checkbox}
                     />
                     Multi-Case Matching (match 3 cases to 3 diagnoses)
                   </label>
                 </div>
              </div>

               <div className={styles.quizControls}>
                 <button type="submit" className={styles.buttonPrimary} disabled={loading}>
                   {loading ? 'Starting Quiz...' : 'Start Quiz'}
                 </button>
               </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Routes>
      <Route path="/" element={<QuizConfigForm />} />
      <Route path="/quiz" element={
        showQuiz && quizConfig ? (
          <QuizPlayer
            quizConfig={quizConfig}
            onQuizComplete={handleQuizComplete}
            onQuizExit={handleQuizExit}
            userId={user?.id}
          />
        ) : (
          <Navigate to="/" replace />
        )
      } />
      <Route path="/cases" element={
        <CaseBrowser
          userId={user?.id}
          onExit={() => window.history.back()}
        />
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;