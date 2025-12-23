import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import QuizComponent from './QuizComponent'; // Reuse the same component with different data

// Sample quiz data for Chapter 2
const chapter2QuizData = {
  title: 'Chapter 2: Humanoid Robotics Fundamentals',
  questions: [
    {
      id: 1,
      question: 'What is kinematics in robotics?',
      options: [
        'The study of motion without considering forces',
        'The study of forces in motion',
        'The study of robot sensors',
        'The study of robot programming'
      ],
      correctAnswer: 0
    },
    {
      id: 2,
      question: 'Which of the following is a common humanoid robot configuration?',
      options: [
        '2 degrees of freedom',
        '4 degrees of freedom',
        '6 degrees of freedom',
        '20+ degrees of freedom'
      ],
      correctAnswer: 3
    },
    {
      id: 3,
      question: 'What is the primary purpose of inverse kinematics?',
      options: [
        'To determine joint angles from end-effector position',
        'To calculate robot speed',
        'To measure robot weight',
        'To determine robot cost'
      ],
      correctAnswer: 0
    }
  ]
};

function Chapter2Quiz() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`${chapter2QuizData.title} Quiz - ${siteConfig.title}`}
      description={`Quiz for ${chapter2QuizData.title}`}>
      <QuizComponent chapterData={chapter2QuizData} />
    </Layout>
  );
}

export default Chapter2Quiz;