import React, { useState } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './create.module.css';

function CreatePage() {
  const { siteConfig } = useDocusaurusContext();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'lesson',
    difficulty: 'beginner'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real implementation, this would save the content
    alert('Content created successfully!');
    setFormData({
      title: '',
      content: '',
      category: 'lesson',
      difficulty: 'beginner'
    });
  };

  return (
    <Layout
      title={`Create Content - ${siteConfig.title}`}
      description="Create new educational content for Physical AI & Humanoid Robotics">
      <main className={styles.createPage}>
        <div className="container">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <div className={styles.header}>
                <h1 className={styles.pageTitle}>Create New Content</h1>
                <p className={styles.pageSubtitle}>Design engaging lessons for Physical AI & Humanoid Robotics</p>
              </div>

              <div className={styles.createCard}>
                <form onSubmit={handleSubmit} className={styles.createForm}>
                  <div className={styles.formGroup}>
                    <label htmlFor="title" className={styles.formLabel}>
                      Title
                    </label>
                    <input
                      type="text"
                      id="title"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className={styles.formInput}
                      placeholder="Enter a compelling title for your content"
                      required
                    />
                  </div>

                  <div className={styles.formGroup}>
                    <label htmlFor="category" className={styles.formLabel}>
                      Category
                    </label>
                    <select
                      id="category"
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                      className={styles.formSelect}
                    >
                      <option value="lesson">Lesson</option>
                      <option value="quiz">Quiz</option>
                      <option value="activity">Activity</option>
                      <option value="project">Project</option>
                      <option value="resource">Resource</option>
                    </select>
                  </div>

                  <div className={styles.formGroup}>
                    <label htmlFor="difficulty" className={styles.formLabel}>
                      Difficulty Level
                    </label>
                    <select
                      id="difficulty"
                      name="difficulty"
                      value={formData.difficulty}
                      onChange={handleInputChange}
                      className={styles.formSelect}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>

                  <div className={styles.formGroup}>
                    <label htmlFor="content" className={styles.formLabel}>
                      Content
                    </label>
                    <textarea
                      id="content"
                      name="content"
                      value={formData.content}
                      onChange={handleInputChange}
                      className={clsx(styles.formInput, styles.formTextarea)}
                      placeholder="Write your content here... Use markdown for formatting."
                      rows={12}
                      required
                    />
                  </div>

                  <div className={styles.formActions}>
                    <button
                      type="submit"
                      className={clsx('button button--primary button--lg', styles.submitButton)}
                    >
                      Create Content
                    </button>
                    <Link
                      to="/"
                      className={clsx('button button--secondary button--lg', styles.cancelButton)}
                    >
                      Cancel
                    </Link>
                  </div>
                </form>
              </div>

              <div className={styles.featuresGrid}>
                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>📚</div>
                  <h3 className={styles.featureTitle}>Educational Focus</h3>
                  <p className={styles.featureDescription}>
                    Create content that helps students understand Physical AI and Humanoid Robotics concepts effectively.
                  </p>
                </div>

                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>🎯</div>
                  <h3 className={styles.featureTitle}>Interactive Elements</h3>
                  <p className={styles.featureDescription}>
                    Include quizzes, activities, and hands-on projects to engage learners.
                  </p>
                </div>

                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>🎨</div>
                  <h3 className={styles.featureTitle}>Visual Appeal</h3>
                  <p className={styles.featureDescription}>
                    Use rich media, diagrams, and interactive elements to enhance learning.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}

export default CreatePage;