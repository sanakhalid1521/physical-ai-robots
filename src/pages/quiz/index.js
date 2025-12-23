import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './quiz.module.css';

function QuizPage() {
  const { siteConfig } = useDocusaurusContext();

  // Sample quiz data - in a real implementation, this would come from a data source
  const chapters = [
    { number: 1, title: 'Introduction to Physical AI', slug: 'chapter-1' },
    { number: 2, title: 'Humanoid Robotics Fundamentals', slug: 'chapter-2' },
    { number: 3, title: 'Sensor Integration & Perception', slug: 'chapter-3' },
    { number: 4, title: 'Control Systems & Actuation', slug: 'chapter-4' },
    { number: 5, title: 'AI Decision Making & Learning', slug: 'chapter-5' },
  ];

  return (
    <Layout
      title={`Quizzes - ${siteConfig.title}`}
      description="Test your knowledge with quizzes for each chapter">
      <main className={styles.quizPage}>
        <div className="container">
          <div className="row">
            <div className="col col--12">
              <h1 className={styles.pageTitle}>Chapter Quizzes</h1>
              <p className={styles.pageSubtitle}>Test your knowledge from each chapter</p>

              <div className={styles.quizList}>
                {chapters.map((chapter) => (
                  <div key={chapter.slug} className={styles.quizCard}>
                    <h3 className={styles.quizCardTitle}>
                      Chapter {chapter.number}: {chapter.title}
                    </h3>
                    <p className={styles.quizCardDescription}>
                      Test your understanding of the concepts covered in Chapter {chapter.number}.
                    </p>
                    <Link
                      to={`/quiz/${chapter.slug}`}
                      className={clsx('button button--primary button--lg', styles.quizCardButton)}
                    >
                      Take Quiz
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}

export default QuizPage;