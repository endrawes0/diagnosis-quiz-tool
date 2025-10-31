import React, { useState } from 'react';
import styles from '../styles/QuizPlayer.module.css';

const MultiCaseMatcher = ({
  question,
  onAnswerSelect,
  selectedAnswer,
  showFeedback = false,
  isSubmitted = false
}) => {
  const [diagnosisPositions, setDiagnosisPositions] = useState({});
  const [draggedDiagnosis, setDraggedDiagnosis] = useState(null);

  const { cases, diagnosis_options } = question;

  const handleDragStart = (e, diagnosis) => {
    setDraggedDiagnosis(diagnosis);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, caseId) => {
    e.preventDefault();
    if (draggedDiagnosis && !isSubmitted) {
      setDiagnosisPositions(prev => ({
        ...prev,
        [caseId]: draggedDiagnosis
      }));
      setDraggedDiagnosis(null);

      // Notify parent of the answer
      const answer = { ...diagnosisPositions, [caseId]: draggedDiagnosis };
      onAnswerSelect(answer);
    }
  };

  const handleDragEnd = () => {
    setDraggedDiagnosis(null);
  };

  const getCaseDiagnosis = (caseId) => {
    return diagnosisPositions[caseId] || null;
  };

  const getAvailableDiagnoses = () => {
    const usedDiagnoses = Object.values(diagnosisPositions);
    return diagnosis_options.filter(diag => !usedDiagnoses.includes(diag));
  };

  const renderCaseColumn = (caseData, index) => {
    const assignedDiagnosis = getCaseDiagnosis(caseData.case_id);

    return (
      <div
        key={caseData.case_id}
        className={styles.caseColumn}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(e, caseData.case_id)}
      >
        <div className={styles.caseCard}>
          <h4>Case {index + 1}</h4>
          <div className={styles.caseDetails}>
            <p><strong>Age:</strong> {caseData.age}</p>
            <p><strong>Chief Complaint:</strong> {caseData.chief_complaint}</p>
            <p><strong>History:</strong> {caseData.history}</p>
            <p><strong>Examination:</strong> {caseData.examination}</p>
          </div>
        </div>
        <div className={styles.diagnosisSlot}>
          {assignedDiagnosis ? (
            <div className={styles.assignedDiagnosis}>
              <span>{assignedDiagnosis.text}</span>
              {!isSubmitted && (
                <button
                  onClick={() => {
                    setDiagnosisPositions(prev => {
                      const newPositions = { ...prev };
                      delete newPositions[caseData.case_id];
                      return newPositions;
                    });
                  }}
                  className={styles.removeButton}
                >
                  ×
                </button>
              )}
            </div>
          ) : (
            <div className={styles.emptySlot}>
              Drop diagnosis here
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.multiCaseContainer}>
      <div className={styles.casesRow}>
        {cases.map((caseData, index) => renderCaseColumn(caseData, index))}
      </div>

      <div className={styles.diagnosesTray}>
        <h4>Available Diagnoses</h4>
        <div className={styles.diagnosesGrid}>
          {getAvailableDiagnoses().map(diagnosis => (
            <div
              key={diagnosis.id}
              draggable={!isSubmitted}
              onDragStart={(e) => handleDragStart(e, diagnosis)}
              onDragEnd={handleDragEnd}
              className={`${styles.diagnosisCard} ${draggedDiagnosis && draggedDiagnosis.id === diagnosis.id ? styles.dragging : ''}`}
            >
              {diagnosis.text}
            </div>
          ))}
        </div>
      </div>

      {showFeedback && (
        <div className={styles.feedback}>
          <h4>Results</h4>
          {cases.map((caseData, index) => {
            const assigned = getCaseDiagnosis(caseData.case_id);
            const correct = question.correct_mapping[caseData.case_id];
            const isCorrect = assigned && assigned.text === correct;

            return (
              <div key={caseData.case_id} className={styles.caseResult}>
                <strong>Case {index + 1}:</strong>
                <span className={isCorrect ? styles.correct : styles.incorrect}>
                  {assigned ? assigned.text : 'No diagnosis assigned'}
                </span>
                {!isCorrect && <span> (Correct: {correct})</span>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MultiCaseMatcher;