import React from 'react';
import styles from '../styles/QuizPlayer.module.css';

const ProgressBar = ({ 
  current, 
  total, 
  showPercentage = true, 
  showText = true,
  height = 8,
  color = '#667eea'
}) => {
  const percentage = total > 0 ? (current / total) * 100 : 0;
  
  return (
    <div className={styles.progressBarContainer}>
      {showText && (
        <div className={styles.progressText}>
          <span>Question {current} of {total}</span>
          {showPercentage && (
            <span>{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div 
        className={styles.progressBar}
        style={{ height: `${height}px` }}
      >
        <div 
          className={styles.progressFill}
          style={{ 
            width: `${percentage}%`,
            backgroundColor: color
          }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;