import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import QuizComponent from './QuizComponent'; // Reuse the same component with different data

// Sample quiz data for Chapter 3
const chapter3QuizData = {
  title: 'Chapter 3: Sensor Integration & Perception',
  questions: [
    {
      id: 1,
      question: 'What is computer vision in robotics?',
      options: [
        'Enabling robots to interpret visual information',
        'Programming robots using visual tools',
        'Using computers to control robots',
        'Creating visual displays for robots'
      ],
      correctAnswer: 0
    },
    {
      id: 2,
      question: 'Which sensor is commonly used for distance measurement?',
      options: [
        'Temperature sensor',
        'Ultrasonic sensor',
        'Pressure sensor',
        'Humidity sensor'
      ],
      correctAnswer: 1
    },
    {
      id: 3,
      question: 'What does SLAM stand for?',
      options: [
        'Simultaneous Localization and Mapping',
        'Systematic Learning and Mapping',
        'Sensor Localization and Mapping',
        'Simple Localization and Mapping'
      ],
      correctAnswer: 0
    }
  ]
};

function Chapter3Quiz() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`${chapter3QuizData.title} Quiz - ${siteConfig.title}`}
      description={`Quiz for ${chapter3QuizData.title}`}>
      <QuizComponent chapterData={chapter3QuizData} />
    </Layout>
  );
}

export default Chapter3Quiz;