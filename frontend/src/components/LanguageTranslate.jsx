import { useEffect, useMemo, useState } from 'react';

const LANGUAGE_OPTIONS = [
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'gu', label: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'pa', label: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം' },
  { code: 'or', label: 'Odia', native: 'ଓଡ଼ିଆ' },
  { code: 'as', label: 'Assamese', native: 'অসমীয়া' },
  { code: 'ur', label: 'Urdu', native: 'اردو' },
  { code: 'ne', label: 'Nepali', native: 'नेपाली' },
  { code: 'mai', label: 'Maithili', native: 'मैथिली' },
  { code: 'bho', label: 'Bhojpuri', native: 'भोजपुरी' },
];

const GOOGLE_ELEMENT_ID = 'google_translate_element';
const GOOGLE_SCRIPT_ID = 'google-translate-script';
const STORAGE_KEY = 'farmsense-language';

function setTranslateCookie(languageCode) {
  const cookieValue = languageCode === 'en' ? '/en/en' : `/en/${languageCode}`;
  const expires = 'expires=Fri, 31 Dec 9999 23:59:59 GMT';

  document.cookie = `googtrans=${cookieValue}; ${expires}; path=/`;
  document.cookie = `googtrans=${cookieValue}; ${expires}; path=/; domain=${window.location.hostname}`;
}

function dispatchGoogleTranslate(languageCode) {
  const combo = document.querySelector('.goog-te-combo');
  if (!combo) return false;

  combo.value = languageCode === 'en' ? '' : languageCode;
  combo.dispatchEvent(new Event('change', { bubbles: true }));
  return true;
}

function loadGoogleTranslate(includedLanguages) {
  if (window.google?.translate?.TranslateElement) return Promise.resolve();

  if (window.__farmsenseGoogleTranslatePromise) {
    return window.__farmsenseGoogleTranslatePromise;
  }

  window.__farmsenseGoogleTranslatePromise = new Promise((resolve, reject) => {
    window.googleTranslateElementInit = () => {
      if (!window.google?.translate?.TranslateElement) {
        reject(new Error('Google Translate failed to initialize'));
        return;
      }

      new window.google.translate.TranslateElement(
        {
          pageLanguage: 'en',
          includedLanguages,
          autoDisplay: false,
          layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
        },
        GOOGLE_ELEMENT_ID
      );
      resolve();
    };

    if (document.getElementById(GOOGLE_SCRIPT_ID)) return;

    const script = document.createElement('script');
    script.id = GOOGLE_SCRIPT_ID;
    script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    script.async = true;
    script.onerror = () => reject(new Error('Could not load translation service'));
    document.body.appendChild(script);
  });

  return window.__farmsenseGoogleTranslatePromise;
}

const TranslateIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="m5 8 6 6" />
    <path d="m4 14 6-6 2-3" />
    <path d="M2 5h12" />
    <path d="M7 2h1" />
    <path d="m22 22-5-10-5 10" />
    <path d="M14 18h6" />
  </svg>
);

export default function LanguageTranslate() {
  const [selected, setSelected] = useState(() => localStorage.getItem(STORAGE_KEY) || 'en');
  const [status, setStatus] = useState('idle');

  const includedLanguages = useMemo(
    () => LANGUAGE_OPTIONS.map((language) => language.code).join(','),
    []
  );

  useEffect(() => {
    loadGoogleTranslate(includedLanguages).catch(() => setStatus('error'));
  }, [includedLanguages]);

  const applyLanguage = async () => {
    setStatus('loading');

    try {
      await loadGoogleTranslate(includedLanguages);
      localStorage.setItem(STORAGE_KEY, selected);
      document.documentElement.lang = selected;
      setTranslateCookie(selected);

      const applied = dispatchGoogleTranslate(selected);
      if (selected === 'en' && !applied) {
        window.location.reload();
        return;
      }

      setStatus(applied ? 'applied' : 'reload');
      if (!applied) window.location.reload();
    } catch {
      setStatus('error');
    }
  };

  return (
    <div className="language-control notranslate" translate="no" aria-label="Page translation controls">
      <div id={GOOGLE_ELEMENT_ID} aria-hidden="true" />
      <select
        className="language-select"
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        aria-label="Choose language"
      >
        <option value="en">English</option>
        {LANGUAGE_OPTIONS.map((language) => (
          <option key={language.code} value={language.code}>
            {language.label} - {language.native}
          </option>
        ))}
      </select>
      <button
        type="button"
        className="language-button"
        onClick={applyLanguage}
        disabled={status === 'loading'}
        title="Translate the page"
        aria-label="Translate the page"
      >
        <TranslateIcon />
        <span>{status === 'loading' ? 'Loading' : 'Translate'}</span>
      </button>
      {status === 'error' && (
        <span className="language-status" role="status">
          Unavailable
        </span>
      )}
    </div>
  );
}
