import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import styles from './QuizButton.module.css';

function QuizButton({ chapterNumber, lessonTitle }) {
  // Generate quiz URL based on chapter number and lesson title
  const quizUrl = `/quiz/chapter-${chapterNumber}`;

  return (
    <div className={styles.quizSection}>
      <div className={styles.quizDivider}></div>
      <div className={styles.quizContent}>
        <h3 className={styles.quizTitle}>Test Your Knowledge</h3>
        <p className={styles.quizDescription}>Ready to test what you've learned? Take the quiz to reinforce your understanding.</p>
        <Link
          to={quizUrl}
          className={clsx('button button--primary button--lg', styles.quizButton)}
        >
          Take Chapter {chapterNumber} Quiz
        </Link>
      </div>
    </div>
  );
}

export default QuizButton;