import React from 'react';
import { useLocation } from '@docusaurus/router';
import { useLocaleContext } from '@docusaurus/theme-common';

const LanguageSwitcher = () => {
  const { locale, setLocale } = useLocaleContext();
  const location = useLocation();

  const switchLanguage = (newLocale) => {
    // Store the current page path
    const currentPath = location.pathname;

    // If we're on the homepage, handle it specially
    let newPath = currentPath;
    if (currentPath === '/' || currentPath === '/en/' || currentPath === '/ur/') {
      newPath = newLocale === 'ur' ? '/ur' : '/en';
    } else {
      // Replace the locale in the path
      if (locale === 'en') {
        newPath = currentPath.replace('/en/', `/${newLocale}/`);
      } else {
        newPath = currentPath.replace('/ur/', `/${newLocale}/`);
      }

      // If the path doesn't contain the current locale, add it
      if (!newPath.includes(`/${newLocale}/`)) {
        newPath = `/${newLocale}${currentPath}`;
      }
    }

    // Update the locale and redirect
    setLocale(newLocale);
    window.location.href = newPath;
  };

  return (
    <div className="language-switcher">
      <button
        className={`lang-btn ${locale === 'en' ? 'active' : ''}`}
        onClick={() => switchLanguage('en')}
        disabled={locale === 'en'}
        title="Switch to English"
      >
        English
      </button>
      <span className="lang-separator">|</span>
      <button
        className={`lang-btn ${locale === 'ur' ? 'active' : ''}`}
        onClick={() => switchLanguage('ur')}
        disabled={locale === 'ur'}
        title="اردو میں تبدیل کریں"
      >
        اردو
      </button>

      <style jsx>{`
        .language-switcher {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem;
          border-radius: 4px;
          background-color: var(--ifm-color-emphasis-100);
        }

        .lang-btn {
          background: none;
          border: 1px solid var(--ifm-color-emphasis-300);
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.85rem;
        }

        .lang-btn:hover:not(:disabled) {
          background-color: var(--ifm-color-emphasis-200);
        }

        .lang-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .lang-btn.active {
          background-color: var(--ifm-color-primary);
          color: white;
          border-color: var(--ifm-color-primary);
        }

        .lang-separator {
          color: var(--ifm-color-emphasis-600);
          user-select: none;
        }
      `}</style>
    </div>
  );
};

export default LanguageSwitcher;