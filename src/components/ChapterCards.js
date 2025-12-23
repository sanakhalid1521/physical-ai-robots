import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './ChapterCards.module.css';

function useCurrentLocale() {
  const { i18n } = useDocusaurusContext();
  return i18n.currentLocale;
}

const ChapterCardsData = [
  {
    title: 'Chapter 1: Introduction to Physical AI',
    description: 'Learn the fundamentals of Physical AI, its applications, and how it differs from traditional AI approaches.',
    to: '/docs/chapter-1/intro',
    urTitle: 'چیپٹر 1: فزیکل اے آئی کا تعارف',
    urDescription: 'فزیکل اے آئی کے بنیادیات، اطلاقیوں، اور روایتی اے آئی کے نقطہ نظر سے کیسے مختلف ہے سیکھیں۔',
    urTo: '/docs/ur/chapter-1/intro',
  },
  {
    title: 'Chapter 2: Humanoid Robotics Fundamentals',
    description: 'Explore the core concepts of humanoid robotics, kinematics, and motion planning.',
    to: '/docs/chapter-2/fundamentals',
    urTitle: 'چیپٹر 2: ہیومنوائڈ روبوٹکس کے بنیادیات',
    urDescription: 'ہیومنوائڈ روبوٹکس، کنیمیٹکس، اور موشن پلاننگ کے بنیادی تصورات کا جائزہ لیں۔',
    urTo: '/docs/ur/chapter-2/fundamentals',
  },
  {
    title: 'Chapter 3: Sensor Integration & Perception',
    description: 'Understand how robots perceive their environment using various sensors and computer vision techniques.',
    to: '/docs/chapter-3/sensors',
    urTitle: 'چیپٹر 3: سینسر انٹیگریشن اور ادراک',
    urDescription: 'سیکھیں کہ روبوٹس مختلف سینسرز اور کمپیوٹر وژن کی تکنیکس کا استعمال کرکے اپنے ماحول کا ادراک کیسے کرتے ہیں۔',
    urTo: '/docs/ur/chapter-3/sensors',
  },
  {
    title: 'Chapter 4: Control Systems & Actuation',
    description: 'Dive into the mechanics of robot control, actuators, and feedback systems for stable movement.',
    to: '/docs/chapter-4/control',
    urTitle: 'چیپٹر 4: کنٹرول سسٹم اور ایکٹو ایشن',
    urDescription: 'روبوٹ کنٹرول، ایکٹو ایٹرز، اور مستحکم حرکت کے لیے فیڈ بیک سسٹم کی میکانکات میں گہرائی سے جائیں۔',
    urTo: '/docs/ur/chapter-4/control',
  },
  {
    title: 'Chapter 5: AI Decision Making & Learning',
    description: 'Discover how AI algorithms enable robots to make decisions and learn from their environment.',
    to: '/docs/chapter-5/ai',
    urTitle: 'چیپٹر 5: اے آئی فیصلہ سازی اور سیکھنا',
    urDescription: 'دریافت کریں کہ اے آئی الگورتھم روبوٹس کو فیصلے کرنے اور اپنے ماحول سے سیکھنے کے قابل کیسے بناتے ہیں۔',
    urTo: '/docs/ur/chapter-5/ai',
  },
];

function ChapterCard({ title, description, to, urTitle, urDescription, urTo }) {
  const currentLocale = useCurrentLocale();

  // Determine which content to show based on locale
  const displayTitle = currentLocale === 'ur' ? urTitle : title;
  const displayDescription = currentLocale === 'ur' ? urDescription : description;
  // Use locale-aware path
  const displayTo = currentLocale === 'ur' ? urTo : to;

  return (
    <div className={clsx('col col--2', styles.chapterCard)}>
      <div className={clsx('card', styles.card)}>
        <div className={clsx('card__image', styles.cardImage)}>
          <img src="/img/card.webp" alt={displayTitle} className={styles.cardImage} />
        </div>
        <div className="card__body">
          <h3 className={styles.cardTitle}>{displayTitle}</h3>
          <p className={styles.cardDescription}>{displayDescription}</p>
        </div>
        <div className="card__footer">
          <Link className={clsx('button button--secondary button--block', styles.cardButton)} to={displayTo}>
            {currentLocale === 'ur' ? 'پڑھنا شروع کریں' : 'Start Reading'}
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function ChapterCards() {
  const currentLocale = useCurrentLocale();

  return (
    <section className={styles.chapterCardsSection}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <h2 className={styles.sectionTitle}>
              {currentLocale === 'ur' ? 'ٹیکسٹ بک چیپٹرز' : 'Textbook Chapters'}
            </h2>
            <p className={styles.sectionSubtitle}>
              {currentLocale === 'ur'
                ? 'فزیکل اے آئی اور ہیومنوائڈ روبوٹکس پر ہمارے جامع منصوبے کا جائزہ لیں'
                : 'Explore our comprehensive curriculum on Physical AI and Humanoid Robotics'}
            </p>
          </div>
        </div>
        <div className="row">
          {ChapterCardsData.map((chapter, index) => (
            <ChapterCard key={index} {...chapter} />
          ))}
        </div>
      </div>
    </section>
  );
}