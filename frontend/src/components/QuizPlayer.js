import React, { useState, useEffect, useCallback } from 'react';
import QuestionDisplay from './QuestionDisplay';
import ProgressBar from './ProgressBar';
import Timer from './Timer';
import ScoreDisplay from './ScoreDisplay';
import { quizAPI } from '../services/api';
import styles from '../styles/QuizPlayer.module.css';

const QuizPlayer = ({
  quizConfig,
  onQuizComplete,
  onQuizExit,
  userId = null
}) => {
  const [quiz, setQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);


  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quizResults, setQuizResults] = useState(null);
  const [timeLeft, setTimeLeft] = useState(60);
  const [streak, setStreak] = useState(0);
  const [totalTime, setTotalTime] = useState(0);

  const currentQuestion = quiz?.quiz_data?.questions?.[currentQuestionIndex];
  const totalQuestions = quiz?.quiz_data?.questions?.length || 0;

  useEffect(() => {
    if (quizConfig) {
      startQuiz();
    }
  }, [quizConfig]);

  const startQuiz = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await quizAPI.generateQuiz(quizConfig);

      if (response.data && response.data.quiz_data) {
        setQuiz(response.data);
        setTimeLeft(quizConfig.untimed_mode ? 0 : (quizConfig.time_per_question || 60));
      } else {
        throw new Error('Invalid response format: missing quiz_data');
      }
    } catch (err) {
      console.error('Quiz generation error:', err);
      let errorMessage = 'Failed to load quiz. Please try again.';

      if (err.response) {
        // Server responded with error
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
        if (err.response.data && err.response.data.message) {
          errorMessage = `Quiz generation failed: ${err.response.data.message}`;
        } else if (err.response.status === 404) {
          errorMessage = 'Quiz service not found. Please check if the backend is running.';
        } else if (err.response.status === 500) {
          errorMessage = 'Server error occurred. Please try again later.';
        }
      } else if (err.request) {
        // Network error
        console.error('Network error:', err.request);
        errorMessage = 'Network error. Please check your connection and ensure the backend is running on localhost:5000.';
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = useCallback((answerId) => {
    if (isSubmitted) return;
    setSelectedAnswer(answerId);
  }, [isSubmitted]);

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || isSubmitted) return;

    // For multi-case matching, check if all cases have diagnoses assigned
    if (currentQuestion.question_type === 'multi_case_matching') {
      const cases = currentQuestion.cases || [];
      const assignedDiagnoses = Object.keys(selectedAnswer || {});
      if (assignedDiagnoses.length !== cases.length) {
        // Not all cases have been assigned
        return;
      }
    } else if (selectedAnswer === null) {
      return;
    }

    setIsSubmitted(true);
    setShowFeedback(true);

    const answerData = {
      question_id: currentQuestion.question_number,
      answer: selectedAnswer,
      time_taken: (60 - timeLeft),
      timestamp: new Date().toISOString()
    };

    try {
      const response = await quizAPI.submitAnswer(quiz.quiz_id, currentQuestion.question_number, selectedAnswer);

      const newAnswers = [...answers, answerData];
      setAnswers(newAnswers);

      // Use the correctness from the backend response
      const isCorrect = response.data.correct;

      if (isCorrect) {
        setStreak(prev => prev + 1);
      } else {
        setStreak(0);
      }

      setTotalTime(prev => prev + (60 - timeLeft));

      setTimeout(() => {
        if (currentQuestionIndex < totalQuestions - 1) {
          moveToNextQuestion();
        } else {
          completeQuiz(newAnswers);
        }
      }, 2000);

    } catch (err) {
      setError('Failed to submit answer. Please try again.');
      console.error('Answer submission error:', err);
      // Reset submission state to allow retry
      setIsSubmitted(false);
      setShowFeedback(false);
    }
  };

  const moveToNextQuestion = () => {
    setCurrentQuestionIndex(prev => prev + 1);
    setSelectedAnswer(null);
    setIsSubmitted(false);
    setShowFeedback(false);
    setTimeLeft(quizConfig?.untimed_mode ? 0 : (quizConfig?.time_per_question || 60));
  };

  const completeQuiz = async (finalAnswers) => {
    setLoading(true);
    
    try {
      const response = await quizAPI.getQuizResults(quiz.quiz_id);
      setQuizResults(response.data);
      
      if (onQuizComplete) {
        onQuizComplete({
          quiz: quiz,
          answers: finalAnswers,
          results: response.data,
          totalTime: totalTime
        });
      }
    } catch (err) {
      setError('Failed to get quiz results. Please try again.');
      console.error('Results fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeUp = () => {
    if (!isSubmitted && !quizConfig?.untimed_mode) {
      // Auto-submit with current selection or null if no selection (only in timed mode)
      handleSubmitAnswer();
    }
  };

  const handleRestart = () => {
    setCurrentQuestionIndex(0);
    setSelectedAnswer(null);
    setAnswers([]);
    setIsSubmitted(false);
    setShowFeedback(false);
    setQuizResults(null);
    setStreak(0);
    setTotalTime(0);
    setTimeLeft(quizConfig?.untimed_mode ? 0 : (quizConfig?.time_per_question || 60));
    startQuiz();
  };

  const handleExit = () => {
    if (onQuizExit) {
      onQuizExit();
    }
  };

  if (loading && !quiz) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error}</p>
          <button className={styles.buttonPrimary} onClick={handleRestart}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (quizResults) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Quiz Complete!</h1>
          <p className={styles.subtitle}>Great job on completing the quiz</p>
        </div>
        
        <div className={styles.quizContainer}>
          <div className={styles.questionContainer}>
            <ScoreDisplay
              score={quizResults.score}
              totalQuestions={totalQuestions}
              correctAnswers={quizResults.correct_answers}
              timeBonus={quizResults.time_bonus}
              streak={streak}
              showDetails={true}
            />
            
            <div className={styles.quizControls}>
              <button className={styles.buttonSecondary} onClick={handleExit}>
                Exit
              </button>
              <button className={styles.buttonPrimary} onClick={handleRestart}>
                Start New Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

if (!quiz || !currentQuestion) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Diagnosis Quiz</h1>
         <p className={styles.subtitle}>Test your knowledge</p>
      </div>

      <div className={styles.quizContainer}>
        <div className={styles.quizHeader}>
          <div className={styles.quizInfo}>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Question</span>
              <span className={styles.infoValue}>
                {currentQuestionIndex + 1}/{totalQuestions}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Score</span>
              <span className={styles.infoValue}>
                {quizResults?.score || 0}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Streak</span>
              <span className={styles.infoValue}>
                {streak} 🔥
              </span>
            </div>
          </div>
          
           <Timer
             initialTime={timeLeft}
             onTimeUp={handleTimeUp}
             isRunning={!isSubmitted}
             warningThreshold={10}
             untimed={quizConfig?.untimed_mode}
           />
        </div>

        <ProgressBar
          current={currentQuestionIndex + 1}
          total={totalQuestions}
          showPercentage={true}
          showText={true}
        />

        <QuestionDisplay
          question={currentQuestion}
          onAnswerSelect={handleAnswerSelect}
          selectedAnswer={selectedAnswer}
          showFeedback={showFeedback}
          isSubmitted={isSubmitted}
        />

        <div className={styles.quizControls}>
          <button className={styles.buttonSecondary} onClick={handleExit}>
            Exit Quiz
          </button>
          
          {!isSubmitted ? (
            <button 
              className={styles.buttonPrimary}
              onClick={handleSubmitAnswer}
              disabled={selectedAnswer === null}
            >
              Submit Answer
            </button>
          ) : (
            <div className={styles.nextButtonContainer}>
              {currentQuestionIndex < totalQuestions - 1 ? (
                <span className={styles.nextQuestionText}>
                  Next question in 2 seconds...
                </span>
              ) : (
                <span className={styles.nextQuestionText}>
                  Completing quiz...
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizPlayer;