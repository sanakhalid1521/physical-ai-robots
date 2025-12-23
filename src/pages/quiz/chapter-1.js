import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import QuizComponent from './QuizComponent'; // Reuse the same component with different data

// Sample quiz data for Chapter 1 - in a real implementation, this would come from a data source
const chapter1QuizData = {
  title: 'Chapter 1: Introduction to Physical AI',
  questions: [
    {
      id: 1,
      question: 'What is Physical AI?',
      options: [
        'A type of artificial intelligence that interacts with the physical world',
        'A branch of robotics',
        'A programming language',
        'A type of sensor'
      ],
      correctAnswer: 0
    },
    {
      id: 2,
      question: 'Which of the following is NOT a key component of Physical AI?',
      options: [
        'Perception systems',
        'Control algorithms',
        'Cloud storage',
        'Actuation mechanisms'
      ],
      correctAnswer: 2
    },
    {
      id: 3,
      question: 'What distinguishes Physical AI from traditional AI?',
      options: [
        'It operates in the physical world',
        'It uses more data',
        'It is faster',
        'It has better algorithms'
      ],
      correctAnswer: 0
    }
  ]
};

// Default export for Chapter 1 with its specific data
export default function Chapter1Quiz() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`${chapter1QuizData.title} Quiz - ${siteConfig.title}`}
      description={`Quiz for ${chapter1QuizData.title}`}>
      <QuizComponent chapterData={chapter1QuizData} />
    </Layout>
  );
}