import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import QuizComponent from './QuizComponent'; // Reuse the same component with different data

// Sample quiz data for Chapter 5
const chapter5QuizData = {
  title: 'Chapter 5: AI Decision Making & Learning',
  questions: [
    {
      id: 1,
      question: 'What is reinforcement learning?',
      options: [
        'Learning through rewards and punishments',
        'Learning by copying others',
        'Learning through supervised examples',
        'Learning through unsupervised clustering'
      ],
      correctAnswer: 0
    },
    {
      id: 2,
      question: 'What is a neural network?',
      options: [
        'A network of computers',
        'A system inspired by biological neural networks',
        'A type of database',
        'A communication protocol'
      ],
      correctAnswer: 1
    },
    {
      id: 3,
      question: 'What is the main goal of AI decision making in robotics?',
      options: [
        'To reduce robot weight',
        'To enable autonomous behavior',
        'To increase robot speed',
        'To decrease robot cost'
      ],
      correctAnswer: 1
    }
  ]
};

function Chapter5Quiz() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`${chapter5QuizData.title} Quiz - ${siteConfig.title}`}
      description={`Quiz for ${chapter5QuizData.title}`}>
      <QuizComponent chapterData={chapter5QuizData} />
    </Layout>
  );
}

export default Chapter5Quiz;