import React, { useState, useEffect, useCallback } from 'react';
import styles from '../styles/QuizPlayer.module.css';

const Timer = ({
  initialTime = 60,
  onTimeUp,
  isRunning = true,
  onTick,
  warningThreshold = 10,
  untimed = false
}) => {
  const [timeLeft, setTimeLeft] = useState(untimed ? 0 : initialTime);
  const [isWarning, setIsWarning] = useState(false);

  useEffect(() => {
    setTimeLeft(untimed ? 0 : initialTime);
    setIsWarning(false);
  }, [initialTime, untimed]);

  useEffect(() => {
    if (!isRunning) {
      return;
    }

    // In untimed mode, never call onTimeUp and count up instead of down
    if (untimed) {
      const timer = setInterval(() => {
        setTimeLeft((prevTime) => {
          const newTime = prevTime + 1;

          if (onTick) {
            onTick(newTime);
          }

          return newTime;
        });
      }, 1000);

      return () => clearInterval(timer);
    }

    // Timed mode: count down
    if (timeLeft <= 0) {
      if (onTimeUp) {
        onTimeUp();
      }
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prevTime) => {
        const newTime = prevTime - 1;

        if (onTick) {
          onTick(newTime);
        }

        if (newTime <= warningThreshold && newTime > 0) {
          setIsWarning(true);
        }

        if (newTime <= 0) {
          if (onTimeUp) {
            onTimeUp();
          }
          return 0;
        }

        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isRunning, timeLeft, onTimeUp, onTick, warningThreshold, untimed]);

  const formatTime = useCallback((seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  const getTimerClass = () => {
    if (!isRunning) return styles.timerPaused;
    if (!untimed && timeLeft <= warningThreshold) return styles.timerWarning;
    return styles.timerNormal;
  };

  return (
    <div className={`${styles.timer} ${getTimerClass()}`}>
      <div className={styles.timerDisplay}>
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={styles.timerIcon}
        >
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        <span className={styles.timerLabel}>
          {untimed ? 'Elapsed:' : 'Time Left:'}
        </span>
        <span className={styles.timerText}>{formatTime(timeLeft)}</span>
      </div>
      {isWarning && !untimed && (
        <div className={styles.timerWarningText}>
          Time running out!
        </div>
      )}
    </div>
  );
};

export default Timer;