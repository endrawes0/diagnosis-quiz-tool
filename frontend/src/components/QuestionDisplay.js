import React, { useState } from 'react';
import MultiCaseMatcher from './MultiCaseMatcher';
import styles from '../styles/QuizPlayer.module.css';

const QuestionDisplay = ({
  question,
  onAnswerSelect,
  selectedAnswer,
  showFeedback = false,
  isSubmitted = false
}) => {
  console.log('QuestionDisplay rendered with:', { question, selectedAnswer, showFeedback, isSubmitted });

  const [hoveredOption, setHoveredOption] = useState(null);

  if (!question) {
    console.log('No question provided to QuestionDisplay');
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  const handleOptionClick = (optionId) => {
    if (!isSubmitted && onAnswerSelect) {
      onAnswerSelect(optionId);
    }
  };

  const getOptionClassName = (optionId) => {
    let className = styles.answerOption;
    
    if (selectedAnswer === optionId && !isSubmitted) {
      className += ` ${styles.selected}`;
    }
    
    if (isSubmitted) {
      if (optionId === question.correct_answer) {
        className += ` ${styles.correct}`;
      } else if (selectedAnswer === optionId && optionId !== question.correct_answer) {
        className += ` ${styles.incorrect}`;
      }
    }
    
    if (hoveredOption === optionId && !isSubmitted) {
      className += ` ${styles.hovered}`;
    }
    
    return className;
  };

  const renderCaseDetails = () => {
    if (!question.case_details) return null;

    return (
      <div className={styles.caseDetails}>
        <h4>Case Details</h4>
        {question.case_details.age && (
          <p><strong>Age:</strong> {question.case_details.age}</p>
        )}
        {question.case_details.gender && (
          <p><strong>Gender:</strong> {question.case_details.gender}</p>
        )}
        {(question.case_details.chief_complaint || question.case_details.history) && <h5>Presentation</h5>}
        {question.case_details.chief_complaint && (
          <p style={{whiteSpace: 'pre-wrap'}}><strong>Chief Complaint:</strong> {question.case_details.chief_complaint}</p>
        )}
        {question.case_details.history && (
          <p style={{whiteSpace: 'pre-wrap'}}><strong>History:</strong> {question.case_details.history}</p>
        )}
        {question.case_details.examination && <h5>MSE</h5>}
        {question.case_details.examination && (
          <p style={{whiteSpace: 'pre-wrap'}}><strong>Examination:</strong> {question.case_details.examination}</p>
        )}
        {question.case_details.vitals && (
          <p style={{whiteSpace: 'pre-wrap'}}><strong>Vitals:</strong> {question.case_details.vitals}</p>
        )}
      </div>
    );
  };

  const renderOptions = () => {
    if (!question.options || !Array.isArray(question.options)) {
      return <p>No options available</p>;
    }

    return question.options.map((option, index) => (
      <button
        key={option.id !== undefined ? option.id : index}
        className={getOptionClassName(option.id !== undefined ? option.id : index)}
        onClick={() => handleOptionClick(option.id !== undefined ? option.id : index)}
        onMouseEnter={() => setHoveredOption(option.id !== undefined ? option.id : index)}
        onMouseLeave={() => setHoveredOption(null)}
        disabled={isSubmitted}
      >
        <span className={styles.answerLabel}>
          {String.fromCharCode(65 + index)}.
        </span>
        {option.text || option}
      </button>
    ));
  };

  const renderFeedback = () => {
    if (!showFeedback || !isSubmitted) return null;

    const isCorrect = selectedAnswer === question.correct_index;
    const correctOption = question.options?.find(opt => opt.id === question.correct_index);

    return (
      <div className={`${styles.feedback} ${isCorrect ? styles.correct : styles.incorrect}`}>
        <h4>{isCorrect ? '✓ Correct!' : '✗ Incorrect'}</h4>
        {question.explanation && (
          <p><strong>Explanation:</strong> {question.explanation}</p>
        )}
        {question.reference && (
          <p><strong>Reference:</strong> {question.reference}</p>
        )}
        {!isCorrect && correctOption && (
          <p><strong>Correct Answer:</strong> {correctOption.text}</p>
        )}
      </div>
    );
  };

  return (
    <div className={styles.questionContainer}>
      <div className={styles.questionHeader}>
        <div className={styles.questionNumber}>
          Question {question.question_number || 'N/A'}
        </div>
        <h2 className={styles.questionText}>
          {question.question_text || question.text}
        </h2>
        {question.difficulty && (
          <div className={styles.difficultyBadge}>
            Difficulty: {question.difficulty}
          </div>
        )}
        {question.category && (
          <div className={styles.categoryBadge}>
            {question.category}
          </div>
        )}
      </div>

      {question.question_type === 'multi_case_matching' ? (
        <MultiCaseMatcher
          question={question}
          onAnswerSelect={onAnswerSelect}
          selectedAnswer={selectedAnswer}
          showFeedback={showFeedback}
          isSubmitted={isSubmitted}
        />
      ) : (
        <>
          {renderCaseDetails()}

          <div className={styles.answersContainer}>
            {renderOptions()}
          </div>
        </>
      )}

      {renderFeedback()}
    </div>
  );
};

export default QuestionDisplay;