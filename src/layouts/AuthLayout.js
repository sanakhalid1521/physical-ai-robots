import React from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

// Custom layout without navbar for auth pages
export default function AuthLayout({ children, title, description }) {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout title={title} description={description}>
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '2rem 0'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '500px',
          margin: '0 auto',
          padding: '0 1rem'
        }}>
          {children}
        </div>
      </div>
    </div>
  );
}