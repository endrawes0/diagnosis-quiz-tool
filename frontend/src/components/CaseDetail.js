import React, { useState, useEffect } from 'react';
import { casesAPI } from '../services/api';
import styles from '../styles/CaseDetail.module.css';

const CaseDetail = ({ case: caseItem, onClose, onStudyMode, userId }) => {
  const [fullCase, setFullCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('narrative');
  const [bookmarked, setBookmarked] = useState(false);
  const [notes, setNotes] = useState('');
  const [userProgress, setUserProgress] = useState(null);

  useEffect(() => {
    if (caseItem) {
      loadFullCase();
      loadUserProgress();
    }
  }, [caseItem]);

  const loadFullCase = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await casesAPI.getCase(caseItem.case_id);
      setFullCase(response.data);
    } catch (err) {
      setError('Failed to load case details');
      console.error('Load case error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUserProgress = async () => {
    try {
      // This would typically call an API to get user progress for this case
      // For now, we'll simulate it
      const progress = {
        completed: false,
        score: null,
        attempts: 0,
        last_attempt: null,
        bookmarked: false,
        notes: ''
      };
      setUserProgress(progress);
      setBookmarked(progress.bookmarked);
      setNotes(progress.notes || '');
    } catch (err) {
      console.error('Load progress error:', err);
    }
  };

  const handleBookmark = async () => {
    try {
      const newBookmarkedState = !bookmarked;
      setBookmarked(newBookmarkedState);
      
      // This would typically call an API to update bookmark status
      await casesAPI.updateBookmark(caseItem.case_id, newBookmarkedState);
      
      if (userProgress) {
        setUserProgress({ ...userProgress, bookmarked: newBookmarkedState });
      }
    } catch (err) {
      setBookmarked(!bookmarked); // Revert on error
      console.error('Bookmark error:', err);
    }
  };

  const handleNotesChange = async (newNotes) => {
    setNotes(newNotes);
    
    try {
      // This would typically call an API to save notes
      await casesAPI.updateNotes(caseItem.case_id, newNotes);
      
      if (userProgress) {
        setUserProgress({ ...userProgress, notes: newNotes });
      }
    } catch (err) {
      console.error('Save notes error:', err);
    }
  };

  const handleStartQuiz = () => {
    // This would navigate to the quiz for this specific case
    console.log('Starting quiz for case:', caseItem.case_id);
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className={styles.caseDetail}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading case details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.caseDetail}>
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={onClose} className={styles.closeButton}>
            Close
          </button>
        </div>
      </div>
    );
  }

  const caseData = fullCase || caseItem;

  return (
    <div className={styles.caseDetail}>
      <div className={styles.caseHeader}>
        <div className={styles.headerContent}>
          <div className={styles.caseInfo}>
            <h1 className={styles.caseTitle}>{caseData.case_id}</h1>
            <div className={styles.caseMeta}>
              <span 
                className={styles.complexityBadge}
                style={{ backgroundColor: getComplexityColor(caseData.complexity) }}
              >
                {caseData.complexity?.replace('_', ' ').toUpperCase()}
              </span>
              <span className={styles.category}>{caseData.category?.replace('_', ' ')}</span>
              <span className={styles.ageGroup}>{caseData.age_group?.replace('_', ' ')}</span>
            </div>
          </div>
          
          <div className={styles.headerActions}>
            <button
              onClick={handleBookmark}
              className={`${styles.bookmarkButton} ${bookmarked ? styles.bookmarked : ''}`}
              title={bookmarked ? 'Remove bookmark' : 'Add bookmark'}
            >
              {bookmarked ? '🔖' : '📁'}
            </button>
            <button
              onClick={onStudyMode}
              className={styles.studyModeButton}
              title="Enter study mode"
            >
              📚 Study Mode
            </button>
            <button
              onClick={onClose}
              className={styles.closeButton}
              title="Close case"
            >
              ✕
            </button>
          </div>
        </div>

        <div className={styles.diagnosisSection}>
          <h2 className={styles.diagnosis}>{caseData.diagnosis}</h2>
          {caseData.diagnosis_details && (
            <div className={styles.diagnosisDetails}>
              <p><strong>Category:</strong> {caseData.diagnosis_details.category}</p>
              <p><strong>Prevalence:</strong> {caseData.diagnosis_details.prevalence_rate}</p>
            </div>
          )}
        </div>
      </div>

      <div className={styles.caseContent}>
        <div className={styles.tabNavigation}>
          <button
            className={`${styles.tabButton} ${activeTab === 'narrative' ? styles.active : ''}`}
            onClick={() => setActiveTab('narrative')}
          >
            Narrative
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'mse' ? styles.active : ''}`}
            onClick={() => setActiveTab('mse')}
          >
            Mental Status Exam
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'notes' ? styles.active : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            Notes
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'progress' ? styles.active : ''}`}
            onClick={() => setActiveTab('progress')}
          >
            Progress
          </button>
        </div>

        <div className={styles.tabContent}>
          {activeTab === 'narrative' && (
            <div className={styles.narrativeTab}>
              <h3>Patient Narrative</h3>
              <div className={styles.narrativeContent}>
                {caseData.narrative?.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'mse' && (
            <div className={styles.mseTab}>
              <h3>Mental Status Examination</h3>
              <div className={styles.mseContent}>
                {caseData.MSE?.split('\n').map((section, index) => (
                  <p key={index}>{section}</p>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className={styles.notesTab}>
              <h3>Personal Notes</h3>
              <textarea
                value={notes}
                onChange={(e) => handleNotesChange(e.target.value)}
                placeholder="Add your notes about this case here..."
                className={styles.notesTextarea}
              />
              <div className={styles.notesInfo}>
                <span>Auto-saved</span>
                <span>{notes.length} characters</span>
              </div>
            </div>
          )}

          {activeTab === 'progress' && (
            <div className={styles.progressTab}>
              <h3>Your Progress</h3>
              {userProgress ? (
                <div className={styles.progressContent}>
                  <div className={styles.progressItem}>
                    <span className={styles.progressLabel}>Status:</span>
                    <span className={styles.progressValue}>
                      {userProgress.completed ? '✅ Completed' : 
                       userProgress.started ? '🔄 In Progress' : '⏸ Not Started'}
                    </span>
                  </div>
                  {userProgress.score !== null && (
                    <div className={styles.progressItem}>
                      <span className={styles.progressLabel}>Best Score:</span>
                      <span className={styles.progressValue}>{userProgress.score}%</span>
                    </div>
                  )}
                  <div className={styles.progressItem}>
                    <span className={styles.progressLabel}>Attempts:</span>
                    <span className={styles.progressValue}>{userProgress.attempts}</span>
                  </div>
                  <div className={styles.progressItem}>
                    <span className={styles.progressLabel}>Last Attempt:</span>
                    <span className={styles.progressValue}>{formatDate(userProgress.last_attempt)}</span>
                  </div>
                </div>
              ) : (
                <p>No progress data available</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className={styles.caseActions}>
        <button
          onClick={handleStartQuiz}
          className={styles.primaryButton}
        >
          Start Quiz
        </button>
        <button
          onClick={onStudyMode}
          className={styles.secondaryButton}
        >
          Study Mode
        </button>
      </div>
    </div>
  );
};

export default CaseDetail;