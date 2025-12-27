import React, { useEffect } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import ChapterCards from '@site/src/components/ChapterCards';

import { useAuth } from '../contexts/AuthContext';
import { usePersonalization } from '../contexts/PersonalizationContext';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  const auth = useAuth();
  const personalization = usePersonalization();
  const { i18n } = useDocusaurusContext();
  const currentLocale = i18n.currentLocale;

  // Handle cases where context might not be available during static generation
  const currentUser = auth?.currentUser || null;
  const logout = auth?.logout || (() => {});
  const preferences = personalization?.preferences || null;


  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.contentWithImage}>
          <div className={styles.heroImageContainer}>
            <img src="/img/hero.jpg" alt="Hero" className={styles.heroImage} />
          </div>
        </div>
        <div className={styles.centeredButton}>
          <Link
            className="button button--secondary button--lg"
            to={currentLocale === 'ur' ? "/docs/ur/intro" : "/docs/intro"}>
            {currentLocale === 'ur' ? "فزیکل اے آئی اور روبوٹکس سیکھیں" : "Start Learning Physical AI & Robotics"}
          </Link>
        </div>
        {currentUser && preferences && (
          <div className={clsx('margin-top--md', styles.userPreferences)}>
            <small>Your content is personalized for your {preferences.programmingLevel} programming level and {preferences.roboticsFamiliarity} robotics familiarity.</small>
          </div>
        )}
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  const { currentUser, loading } = useAuth();

  // If user is authenticated, show the home page; otherwise, show the home page anyway
  // The authentication will be handled by individual protected routes
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into the meta tag">
      <HomepageHeader />
      <main>
        <ChapterCards />
        <HomepageFeatures />
      </main>
    </Layout>
  );
}