import React, { useState } from 'react';
import styles from '../styles/CaseCard.module.css';

const CaseCard = ({
  case: caseItem,
  onSelect,
  onStudyMode,
  viewMode,
  getComplexityColor,
  getAgeGroupIcon,
  userProgress
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCardClick = () => {
    onSelect();
  };

  const handleStudyModeClick = (e) => {
    e.stopPropagation();
    onStudyMode();
  };

  const getCompletionStatus = () => {
    if (!userProgress) return 'not_started';
    if (userProgress.completed) return 'completed';
    if (userProgress.started) return 'in_progress';
    return 'not_started';
  };

  const getStatusColor = () => {
    const status = getCompletionStatus();
    const colors = {
      completed: '#4CAF50',
      in_progress: '#FF9800',
      not_started: '#9E9E9E'
    };
    return colors[status];
  };

  const getStatusText = () => {
    const status = getCompletionStatus();
    const texts = {
      completed: 'Completed',
      in_progress: 'In Progress',
      not_started: 'Not Started'
    };
    return texts[status];
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div
      className={`${styles.caseCard} ${styles[viewMode]} ${isHovered ? styles.hovered : ''}`}
      onClick={handleCardClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={styles.cardHeader}>
        <div className={styles.caseInfo}>
          <span className={styles.caseId}>{caseItem.case_id}</span>
          <span 
            className={styles.complexityBadge}
            style={{ backgroundColor: getComplexityColor(caseItem.complexity) }}
          >
            {caseItem.complexity?.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <div className={styles.statusIndicator}>
          <div 
            className={styles.statusDot}
            style={{ backgroundColor: getStatusColor() }}
            title={getStatusText()}
          />
        </div>
      </div>

      <div className={styles.cardContent}>
        <div className={styles.caseMeta}>
          <span className={styles.ageGroup}>
            {getAgeGroupIcon(caseItem.age_group)} {caseItem.age_group?.replace('_', ' ')}
          </span>
          <span className={styles.category}>{caseItem.category?.replace('_', ' ')}</span>
        </div>

         <h3 className={styles.diagnosis}>{caseItem.diagnosis}</h3>

         <div className={styles.narrativeContainer}>
           <p className={`${styles.narrative} ${isExpanded ? styles.expanded : styles.collapsed}`}>
             {caseItem.narrative_preview || caseItem.narrative}
           </p>
           {(caseItem.narrative_preview || caseItem.narrative) && (caseItem.narrative_preview || caseItem.narrative).length > 150 && (
             <button
               className={styles.expandButton}
               onClick={(e) => {
                 e.stopPropagation();
                 setIsExpanded(!isExpanded);
               }}
             >
               {isExpanded ? 'Show Less' : 'Show More'}
             </button>
           )}
         </div>

        {caseItem.mse_preview && (
          <div className={styles.mseSection}>
            <span className={styles.mseLabel}>MSE:</span>
            <span className={styles.mseText}>{caseItem.mse_preview}</span>
          </div>
        )}

        {userProgress && (
          <div className={styles.progressInfo}>
            {userProgress.score !== undefined && (
              <span className={styles.score}>
                Score: {userProgress.score}%
              </span>
            )}
            {userProgress.attempts && (
              <span className={styles.attempts}>
                Attempts: {userProgress.attempts}
              </span>
            )}
            {userProgress.last_attempt && (
              <span className={styles.lastAttempt}>
                Last: {formatDate(userProgress.last_attempt)}
              </span>
            )}
          </div>
        )}

        {caseItem.relevance_score && (
          <div className={styles.relevanceScore}>
            Relevance: {Math.round(caseItem.relevance_score * 10)}%
          </div>
        )}
      </div>

      <div className={styles.cardActions}>
        <button 
          className={styles.primaryButton}
          onClick={handleCardClick}
        >
          View Case
        </button>
        <button 
          className={styles.secondaryButton}
          onClick={handleStudyModeClick}
        >
          Study Mode
        </button>
      </div>

      {isHovered && (
        <div className={styles.quickInfo}>
          <div className={styles.quickInfoItem}>
            <span className={styles.quickInfoLabel}>XP:</span>
            <span className={styles.quickInfoValue}>
              {caseItem.xp_value || '10'}
            </span>
          </div>
          <div className={styles.quickInfoItem}>
            <span className={styles.quickInfoLabel}>Time:</span>
            <span className={styles.quickInfoValue}>
              {caseItem.estimated_time || '5-10 min'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseCard;