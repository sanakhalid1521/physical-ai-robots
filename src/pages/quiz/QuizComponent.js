import React, { useState } from 'react';
import clsx from 'clsx';
import styles from './chapter-quiz.module.css';

// Reusable quiz component without Layout wrapper for other chapters to import
function QuizComponent({ chapterData }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const handleAnswerChange = (questionId, optionIndex) => {
    if (!submitted) {
      setAnswers(prev => ({
        ...prev,
        [questionId]: optionIndex
      }));
    }
  };

  const handleSubmit = () => {
    let correctCount = 0;
    chapterData.questions.forEach(question => {
      if (answers[question.id] === question.correctAnswer) {
        correctCount++;
      }
    });
    setScore(correctCount);
    setSubmitted(true);
  };

  const handleReset = () => {
    setAnswers({});
    setSubmitted(false);
    setScore(0);
  };

  return (
    <main className={styles.quizPage}>
      <div className="container">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <h1 className={styles.quizTitle}>{chapterData.title} Quiz</h1>

            <div className={styles.questionsContainer}>
              {chapterData.questions.map((question, index) => (
                <div key={question.id} className={styles.questionCard}>
                  <h3 className={styles.questionNumber}>Question {index + 1}</h3>
                  <p className={styles.questionText}>{question.question}</p>

                  <div className={styles.optionsContainer}>
                    {question.options.map((option, optionIndex) => {
                      const isSelected = answers[question.id] === optionIndex;
                      const isCorrect = optionIndex === question.correctAnswer;
                      const showResult = submitted;

                      let optionClass = styles.option;

                      if (showResult) {
                        if (isCorrect) {
                          optionClass = clsx(optionClass, styles.optionCorrect);
                        } else if (isSelected && !isCorrect) {
                          optionClass = clsx(optionClass, styles.optionIncorrect);
                        }
                      } else if (isSelected) {
                        optionClass = clsx(optionClass, styles.optionSelected);
                      }

                      return (
                        <label
                          key={optionIndex}
                          className={optionClass}
                        >
                          <input
                            type="radio"
                            name={`question-${question.id}`}
                            value={optionIndex}
                            checked={isSelected}
                            disabled={submitted}
                            onChange={() => handleAnswerChange(question.id, optionIndex)}
                            className={styles.optionInput}
                          />
                          <span className={styles.optionText}>{option}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <div className={styles.actionsContainer}>
              {!submitted ? (
                <button
                  className={clsx('button button--primary button--lg', styles.submitButton)}
                  onClick={handleSubmit}
                  disabled={chapterData.questions.length !== Object.keys(answers).length}
                >
                  Submit Quiz
                </button>
              ) : (
                <div className={styles.resultsContainer}>
                  <h3 className={styles.resultsTitle}>
                    Your Score: {score} out of {chapterData.questions.length}
                  </h3>
                  <p className={styles.resultsMessage}>
                    {score === chapterData.questions.length
                      ? 'Excellent! You mastered this chapter.'
                      : score >= chapterData.questions.length / 2
                        ? 'Good job! Review the material to improve.'
                        : 'Keep studying! You can do better next time.'}
                  </p>
                  <button
                    className={clsx('button button--secondary button--lg', styles.resetButton)}
                    onClick={handleReset}
                  >
                    Retake Quiz
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default QuizComponent;