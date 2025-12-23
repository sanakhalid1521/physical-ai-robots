import React from 'react';
import {useLocation} from '@docusaurus/router';
import {translate} from '@docusaurus/Translate';

function LanguageSwitcherNavbarItem({mobile = false}) {
  const location = useLocation();

  // Get available locales from docusaurus config
  const locales = ['en', 'ur'];
  const currentLocale = location.pathname.split('/')[1] || 'en';

  const switchLocale = (locale) => {
    // Determine the new path by replacing the current locale
    let newPath = location.pathname;
    if (currentLocale === 'en' && locale === 'ur') {
      newPath = `/ur${location.pathname}`;
    } else if (currentLocale === 'ur') {
      newPath = location.pathname.replace('/ur/', '/');
    } else if (currentLocale !== 'ur' && locale === 'ur') {
      newPath = `/ur${location.pathname}`;
    }

    // Preserve query parameters and hash
    const search = location.search || '';
    const hash = location.hash || '';

    window.location.href = `${newPath}${search}${hash}`;
  };

  return (
    <div className={`navbar__item navbar__dropdown ${mobile ? 'navbar__dropdown--mobile' : ''}`}>
      <select
        value={currentLocale}
        onChange={(e) => switchLocale(e.target.value)}
        className="navbar__select"
        style={{ border: 'none', background: 'transparent', color: 'white', cursor: 'pointer' }}
      >
        {locales.map((locale) => (
          <option key={locale} value={locale}>
            {locale === 'en' ? 'English' : 'اردو'}
          </option>
        ))}
      </select>
    </div>
  );
}

export default LanguageSwitcherNavbarItem;