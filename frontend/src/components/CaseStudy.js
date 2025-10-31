import React, { useState, useEffect } from 'react';
import { casesAPI } from '../services/api';
import styles from '../styles/CaseStudy.module.css';

const CaseStudy = ({ case: caseItem, onClose, userId }) => {
  const [fullCase, setFullCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [studyMode, setStudyMode] = useState('analysis'); // 'analysis', 'quiz', 'review'
  const [currentStep, setCurrentStep] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [notes, setNotes] = useState('');
  const [bookmarks, setBookmarks] = useState([]);
  const [timer, setTimer] = useState(0);
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [highlightedText, setHighlightedText] = useState([]);

  const studySteps = [
    { id: 'initial', title: 'Initial Assessment', description: 'Read the case and form initial impressions' },
    { id: 'analysis', title: 'Detailed Analysis', description: 'Analyze symptoms and identify key findings' },
    { id: 'differential', title: 'Differential Diagnosis', description: 'Consider possible diagnoses' },
    { id: 'final', title: 'Final Diagnosis', description: 'Make your final diagnosis and treatment plan' }
  ];

  useEffect(() => {
    if (caseItem) {
      loadFullCase();
      startTimer();
    }
    return () => stopTimer();
  }, [caseItem]);

  useEffect(() => {
    let interval;
    if (isTimerActive) {
      interval = setInterval(() => {
        setTimer(timer => timer + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerActive]);

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

  const startTimer = () => {
    setIsTimerActive(true);
  };

  const stopTimer = () => {
    setIsTimerActive(false);
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStepChange = (stepIndex) => {
    setCurrentStep(stepIndex);
  };

  const handleAnswerChange = (questionId, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    if (selectedText) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      // Add highlight
      setHighlightedText(prev => [...prev, {
        text: selectedText,
        range: range.toString(),
        timestamp: Date.now()
      }]);
      
      // Show annotation dialog (simplified)
      const note = prompt('Add a note for this selection:');
      if (note) {
        setNotes(prev => prev + `\n\nHighlighted: "${selectedText}"\nNote: ${note}`);
      }
      
      selection.removeAllRanges();
    }
  };

  const handleBookmark = (content) => {
    setBookmarks(prev => [...prev, {
      content,
      timestamp: Date.now(),
      step: studySteps[currentStep].id
    }]);
  };

  const handleCompleteStudy = () => {
    setShowResults(true);
    stopTimer();
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

  const calculateProgress = () => {
    return ((currentStep + 1) / studySteps.length) * 100;
  };

  if (loading) {
    return (
      <div className={styles.caseStudy}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading study mode...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.caseStudy}>
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
    <div className={styles.caseStudy}>
      <div className={styles.studyHeader}>
        <div className={styles.headerContent}>
          <div className={styles.caseInfo}>
            <h1 className={styles.caseTitle}>Study Mode: {caseData.case_id}</h1>
            <div className={styles.studyMeta}>
              <span 
                className={styles.complexityBadge}
                style={{ backgroundColor: getComplexityColor(caseData.complexity) }}
              >
                {caseData.complexity?.replace('_', ' ').toUpperCase()}
              </span>
              <span className={styles.timer}>{formatTime(timer)}</span>
              <span className={styles.progress}>
                Step {currentStep + 1} of {studySteps.length}
              </span>
            </div>
          </div>
          
          <div className={styles.headerActions}>
            <button
              onClick={() => handleBookmark(caseData.narrative)}
              className={styles.bookmarkButton}
              title="Add bookmark"
            >
              🔖
            </button>
            <button
              onClick={onClose}
              className={styles.closeButton}
              title="Exit study mode"
            >
              ✕
            </button>
          </div>
        </div>

        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill}
            style={{ width: `${calculateProgress()}%` }}
          />
        </div>

        <div className={styles.stepNavigation}>
          {studySteps.map((step, index) => (
            <button
              key={step.id}
              className={`${styles.stepButton} ${index === currentStep ? styles.active : ''} ${index < currentStep ? styles.completed : ''}`}
              onClick={() => handleStepChange(index)}
            >
              <div className={styles.stepNumber}>{index + 1}</div>
              <div className={styles.stepInfo}>
                <div className={styles.stepTitle}>{step.title}</div>
                <div className={styles.stepDescription}>{step.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className={styles.studyContent}>
        <div className={styles.contentArea}>
          <div className={styles.caseContent}>
            <div className={styles.contentSection}>
              <h3>Patient Narrative</h3>
              <div 
                className={styles.narrativeText}
                onMouseUp={handleTextSelection}
              >
                {caseData.narrative?.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>

            <div className={styles.contentSection}>
              <h3>Mental Status Examination</h3>
              <div 
                className={styles.mseText}
                onMouseUp={handleTextSelection}
              >
                {caseData.MSE?.split('\n').map((section, index) => (
                  <p key={index}>{section}</p>
                ))}
              </div>
            </div>
          </div>

          <div className={styles.studyPanel}>
            <div className={styles.panelSection}>
              <h3>Study Notes</h3>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Take notes as you study this case..."
                className={styles.notesTextarea}
              />
            </div>

            <div className={styles.panelSection}>
              <h3>Key Questions</h3>
              <div className={styles.questionsList}>
                <div className={styles.question}>
                  <p>What are the most significant symptoms in this case?</p>
                  <textarea
                    value={userAnswers.q1 || ''}
                    onChange={(e) => handleAnswerChange('q1', e.target.value)}
                    placeholder="Your analysis..."
                    className={styles.answerTextarea}
                  />
                </div>
                <div className={styles.question}>
                  <p>What differential diagnoses would you consider?</p>
                  <textarea
                    value={userAnswers.q2 || ''}
                    onChange={(e) => handleAnswerChange('q2', e.target.value)}
                    placeholder="List possible diagnoses..."
                    className={styles.answerTextarea}
                  />
                </div>
                <div className={styles.question}>
                  <p>What additional information would you need?</p>
                  <textarea
                    value={userAnswers.q3 || ''}
                    onChange={(e) => handleAnswerChange('q3', e.target.value)}
                    placeholder="What questions would you ask..."
                    className={styles.answerTextarea}
                  />
                </div>
              </div>
            </div>

            {bookmarks.length > 0 && (
              <div className={styles.panelSection}>
                <h3>Bookmarks</h3>
                <div className={styles.bookmarksList}>
                  {bookmarks.map((bookmark, index) => (
                    <div key={index} className={styles.bookmarkItem}>
                      <p>{bookmark.content.substring(0, 100)}...</p>
                      <small>Step: {bookmark.step}</small>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className={styles.studyActions}>
        <button
          onClick={() => handleStepChange(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className={styles.secondaryButton}
        >
          Previous Step
        </button>
        
        {currentStep < studySteps.length - 1 ? (
          <button
            onClick={() => handleStepChange(currentStep + 1)}
            className={styles.primaryButton}
          >
            Next Step
          </button>
        ) : (
          <button
            onClick={handleCompleteStudy}
            className={styles.completeButton}
          >
            Complete Study
          </button>
        )}
      </div>

      {showResults && (
        <div className={styles.resultsModal}>
          <div className={styles.resultsContent}>
            <h2>Study Session Complete!</h2>
            <div className={styles.resultsSummary}>
              <p><strong>Time Spent:</strong> {formatTime(timer)}</p>
              <p><strong>Notes Written:</strong> {notes.length} characters</p>
              <p><strong>Bookmarks Created:</strong> {bookmarks.length}</p>
              <p><strong>Questions Answered:</strong> {Object.keys(userAnswers).length}</p>
            </div>
            <div className={styles.resultsActions}>
              <button
                onClick={() => {
                  setShowResults(false);
                  // This would typically save the study session
                }}
                className={styles.primaryButton}
              >
                Save Session
              </button>
              <button
                onClick={onClose}
                className={styles.secondaryButton}
              >
                Exit Study Mode
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseStudy;