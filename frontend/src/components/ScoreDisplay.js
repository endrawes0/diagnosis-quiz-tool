import React from 'react';
import styles from '../styles/QuizPlayer.module.css';

const ScoreDisplay = ({ 
  score, 
  totalQuestions, 
  correctAnswers, 
  timeBonus = 0,
  streak = 0,
  showDetails = true 
}) => {
  const percentage = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
  const totalScore = score + timeBonus;
  
  const getScoreColor = (percentage) => {
    if (percentage >= 90) return '#28a745';
    if (percentage >= 70) return '#ffc107';
    if (percentage >= 50) return '#fd7e14';
    return '#dc3545';
  };

  const getGrade = (percentage) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 85) return 'A';
    if (percentage >= 80) return 'A-';
    if (percentage >= 75) return 'B+';
    if (percentage >= 70) return 'B';
    if (percentage >= 65) return 'B-';
    if (percentage >= 60) return 'C+';
    if (percentage >= 55) return 'C';
    if (percentage >= 50) return 'C-';
    return 'D';
  };

  return (
    <div className={styles.scoreDisplay}>
      <div className={styles.scoreMain}>
        <div className={styles.scoreValue}>
          {totalScore}
        </div>
        <div className={styles.scoreLabel}>
          Total Score
        </div>
      </div>
      
      {showDetails && (
        <div className={styles.scoreDetails}>
          <div className={styles.scoreItem}>
            <span className={styles.scoreItemLabel}>Accuracy:</span>
            <span 
              className={styles.scoreItemValue}
              style={{ color: getScoreColor(percentage) }}
            >
              {correctAnswers}/{totalQuestions} ({percentage}%)
            </span>
          </div>
          
          {timeBonus > 0 && (
            <div className={styles.scoreItem}>
              <span className={styles.scoreItemLabel}>Time Bonus:</span>
              <span className={styles.scoreItemValue}>+{timeBonus}</span>
            </div>
          )}
          
          {streak > 1 && (
            <div className={styles.scoreItem}>
              <span className={styles.scoreItemLabel}>Streak:</span>
              <span className={styles.scoreItemValue}>{streak} 🔥</span>
            </div>
          )}
          
          <div className={styles.scoreItem}>
            <span className={styles.scoreItemLabel}>Grade:</span>
            <span 
              className={styles.scoreGrade}
              style={{ 
                backgroundColor: getScoreColor(percentage),
                color: 'white'
              }}
            >
              {getGrade(percentage)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScoreDisplay;