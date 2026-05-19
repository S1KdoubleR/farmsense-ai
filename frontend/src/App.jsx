/**
 * App.jsx — FarmSense AI v2.0
 * Root application component — premium enterprise redesign, no emojis.
 */
import { useState, useEffect } from 'react';
import InputForm from './components/InputForm';
import LanguageTranslate from './components/LanguageTranslate';
import ResultsPanel from './components/ResultsPanel';
import { predictCrops, getHealth } from './api';

// ── SVG Icons ──────────────────────────────────────────────────────────────
const LeafIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
  </svg>
);

const CircleIcon = ({ size = 8 }) => (
  <div style={{ width: size, height: size, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
);

// ── Animated background ──────────────────────────────────────────────────
function Background() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Large radial glow spots */}
      <div className="absolute rounded-full animate-pulse-slow" style={{
        width: '800px', height: '800px',
        top: '-300px', left: '-200px',
        background: 'radial-gradient(circle, rgba(74,153,67,0.05) 0%, transparent 65%)',
      }} />
      <div className="absolute rounded-full animate-pulse-slow" style={{
        width: '600px', height: '600px',
        bottom: '-200px', right: '-150px',
        background: 'radial-gradient(circle, rgba(74,153,67,0.04) 0%, transparent 70%)',
        animationDelay: '2s',
      }} />
      <div className="absolute rounded-full animate-pulse-slow" style={{
        width: '400px', height: '400px',
        top: '40%', right: '10%',
        background: 'radial-gradient(circle, rgba(212,168,67,0.03) 0%, transparent 70%)',
        animationDelay: '1s',
      }} />
      {/* Fine grid */}
      <div className="absolute inset-0" style={{
        backgroundImage: 'linear-gradient(rgba(74,153,67,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(74,153,67,0.025) 1px, transparent 1px)',
        backgroundSize: '80px 80px',
      }} />
    </div>
  );
}

// ── Backend Status Indicator ─────────────────────────────────────────────
function BackendStatus({ status }) {
  const configs = {
    checking: { color: '#4d6b49', label: 'Connecting' },
    online:   { color: '#5dbf55', label: 'System Online' },
    offline:  { color: '#c0392b', label: 'System Offline' },
  };
  const { color, label } = configs[status];
  return (
    <div className="flex items-center gap-2">
      <div style={{
        width: 7, height: 7, borderRadius: '50%',
        background: color,
        boxShadow: status === 'online' ? `0 0 8px ${color}` : 'none',
      }} />
      <span style={{
        color,
        fontFamily: 'Space Mono, monospace',
        fontSize: 11,
        letterSpacing: '0.06em',
        fontWeight: 700,
        textTransform: 'uppercase',
      }}>{label}</span>
    </div>
  );
}

// ── Main App ─────────────────────────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState('input');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [submittedParams, setSubmittedParams] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const checkBackend = async () => {
      try {
        await getHealth();
        if (!cancelled) setBackendStatus('online');
      } catch {
        if (!cancelled) setBackendStatus('offline');
      }
    };

    checkBackend();
    const intervalId = window.setInterval(checkBackend, 15000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  const handleSubmit = async (params) => {
    setLoading(true);
    setError('');
    setSubmittedParams(params);
    try {
      const data = await predictCrops(params);
      setResults(data);
      setScreen('results');
    } catch (err) {
      setError(`Analysis failed: ${err.message} — Ensure the backend is running on port 8001.`);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setScreen('input');
    setResults(null);
    setError('');
  };

  return (
    <div className="relative min-h-screen noise-overlay" style={{ background: 'var(--bg-base)' }}>
      <Background />

      {/* ── Header */}
      <header className="relative z-10 sticky top-0" style={{
        background: 'rgba(6, 13, 5, 0.9)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div className="max-w-5xl mx-auto px-6 min-h-[60px] py-3 flex items-center justify-between gap-4 app-header-inner">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div style={{
              width: 34, height: 34,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #3d8038, #5dbf55)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 16px rgba(74,153,67,0.3)',
              color: '#fff',
              flexShrink: 0,
            }}>
              <LeafIcon />
            </div>
            <div>
              <h1 style={{
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: 17, fontWeight: 700,
                background: 'linear-gradient(135deg, #7dd977, #d4a843)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                lineHeight: 1, margin: 0,
              }}>FarmSense AI</h1>
              <p style={{
                fontFamily: 'Space Mono, monospace',
                fontSize: 10, color: 'var(--text-muted)',
                margin: '2px 0 0',
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
              }}>Agricultural Intelligence Platform</p>
            </div>
          </div>

          {/* Right */}
          <div className="flex items-center gap-4 app-header-actions">
            <BackendStatus status={backendStatus} />
            <LanguageTranslate />
            {screen === 'results' && (
              <span style={{
                fontFamily: 'Space Mono, monospace',
                fontSize: 11, color: 'var(--accent-bright)',
                background: 'rgba(74,153,67,0.1)',
                border: '1px solid var(--border-mid)',
                padding: '4px 10px', borderRadius: 6,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
              }}>Results</span>
            )}
          </div>
        </div>
      </header>

      {/* ── Main */}
      <main className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-10">
        {/* Hero — input screen only */}
        {screen === 'input' && (
          <div className="mb-10 text-center">
            {/* Category pill */}
            <div className="inline-flex items-center gap-2 mb-5" style={{
              background: 'rgba(74,153,67,0.07)',
              border: '1px solid var(--border-mid)',
              borderRadius: 20, padding: '5px 14px',
            }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--accent-bright)',
                boxShadow: '0 0 8px rgba(93,191,85,0.7)',
              }} />
              <span style={{
                fontFamily: 'Space Mono, monospace',
                fontSize: 11, color: 'var(--accent-bright)',
                letterSpacing: '0.06em', fontWeight: 700,
                textTransform: 'uppercase',
              }}>AI-Powered · 56 Indian Crops · Live Weather Integration</span>
            </div>

            <h2 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: 'clamp(36px, 5vw, 56px)',
              fontWeight: 800,
              lineHeight: 1.1,
              margin: '0 0 16px',
              letterSpacing: '-0.02em',
            }}>
              Precision Crop{' '}
              <span className="gradient-text">Intelligence</span>
            </h2>
            <p style={{
              color: 'var(--text-secondary)',
              fontSize: 16, lineHeight: 1.6,
              maxWidth: 540, margin: '0 auto 28px',
              fontFamily: 'Inter, sans-serif',
            }}>
              Enter your soil parameters, location, and farm economics. Our ML system analyzes
              11 parameters across 56 crops to recommend the most profitable options for your land.
            </p>

            {/* Feature strip */}
            <div className="flex flex-wrap justify-center gap-3">
              {[
                'Real-time Weather API',
                'Soil Report OCR Upload',
                'Score-Threshold Filtering',
                'Revenue Projections',
                'Government Schemes',
              ].map((f) => (
                <span key={f} style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 12, fontWeight: 600,
                  color: 'var(--text-secondary)',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--border-subtle)',
                  padding: '6px 14px', borderRadius: 20,
                }}>{f}</span>
              ))}
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="mb-6 rounded-2xl p-4 flex items-start gap-4 animate-fade-in" style={{
            background: 'var(--red-error-bg)',
            border: '1px solid rgba(192,57,43,0.3)',
          }} role="alert">
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: 'rgba(192,57,43,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c0392b" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div>
              <p style={{ color: '#c0392b', fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 14, margin: '0 0 4px' }}>
                Analysis Failed
              </p>
              <p style={{ color: 'var(--text-secondary)', fontFamily: 'Space Mono, monospace', fontSize: 12, margin: 0 }}>
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Screens */}
        {screen === 'input' && (
          <div className="glass-elevated rounded-3xl glow-card" style={{ padding: '32px', border: '1px solid var(--border-subtle)' }}>
            <InputForm onSubmit={handleSubmit} loading={loading} />
          </div>
        )}

        {screen === 'results' && results && (
          <ResultsPanel results={results} onBack={handleBack} inputParams={submittedParams} />
        )}
      </main>

      {/* ── Footer */}
      <footer className="relative z-10 text-center py-8 mt-4" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <p style={{
          fontFamily: 'Space Mono, monospace',
          fontSize: 11, color: 'var(--text-muted)',
          letterSpacing: '0.04em',
        }}>
          FarmSense AI v2.0 · Random Forest ML · Open-Meteo Weather · Agmarknet Price Data · Built for Indian Agriculture
        </p>
      </footer>
    </div>
  );
}
