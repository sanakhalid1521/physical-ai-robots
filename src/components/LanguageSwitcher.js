import React from 'react';
import { useLocation } from '@docusaurus/router';

const LanguageSwitcher = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  // Function to switch to English
  const switchToEnglish = () => {
    if (currentPath.startsWith('/docs/ur/')) {
      const newPath = currentPath.replace('/docs/ur/', '/docs/');
      window.location.href = newPath;
    } else if (currentPath.startsWith('/ur/')) {
      const newPath = currentPath.replace('/ur/', '/');
      window.location.href = newPath;
    } else if (currentPath === '/ur' || currentPath === '/ur/') {
      window.location.href = '/';
    } else {
      window.location.href = currentPath; // Stay on the same page but in English
    }
  };

  // Function to switch to Urdu
  const switchToUrdu = () => {
    if (currentPath.startsWith('/docs/') && !currentPath.startsWith('/docs/ur/')) {
      const newPath = currentPath.replace('/docs/', '/docs/ur/');
      window.location.href = newPath;
    } else if (!currentPath.startsWith('/ur/') && currentPath !== '/') {
      const newPath = currentPath.replace('/', '/ur/');
      window.location.href = newPath;
    } else if (currentPath === '/' || currentPath === '') {
      window.location.href = '/ur';
    } else {
      window.location.href = currentPath; // Stay on the same page but in Urdu
    }
  };

  // Determine current language based on path
  const isUrdu = currentPath.startsWith('/docs/ur/') || currentPath.startsWith('/ur/');

  return (
    <div className="navbar__item dropdown dropdown--right dropdown--lang">
      <button
        className="button button--secondary navbar__link"
        onClick={() => isUrdu ? switchToEnglish() : switchToUrdu()}
        style={{
          backgroundColor: isUrdu ? '#FF00FF' : '#FF69B4',
          color: 'white',
          border: 'none',
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {isUrdu ? 'English' : 'اردو'}
      </button>
    </div>
  );
};

export default LanguageSwitcher;