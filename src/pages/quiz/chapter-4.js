import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import QuizComponent from './QuizComponent'; // Reuse the same component with different data

// Sample quiz data for Chapter 4
const chapter4QuizData = {
  title: 'Chapter 4: Control Systems & Actuation',
  questions: [
    {
      id: 1,
      question: 'What is a PID controller?',
      options: [
        'Proportional Integral Derivative controller',
        'Power Input Drive controller',
        'Programmable Interface Device',
        'Precision Input Detection'
      ],
      correctAnswer: 0
    },
    {
      id: 2,
      question: 'What is the role of an actuator in robotics?',
      options: [
        'To sense the environment',
        'To process information',
        'To create motion or control systems',
        'To store data'
      ],
      correctAnswer: 2
    },
    {
      id: 3,
      question: 'What is feedback control?',
      options: [
        'Control without measurement',
        'Control using system output to adjust input',
        'Control using random inputs',
        'Control using only initial conditions'
      ],
      correctAnswer: 1
    }
  ]
};

function Chapter4Quiz() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`${chapter4QuizData.title} Quiz - ${siteConfig.title}`}
      description={`Quiz for ${chapter4QuizData.title}`}>
      <QuizComponent chapterData={chapter4QuizData} />
    </Layout>
  );
}

export default Chapter4Quiz;