/**
 * ResultsPanel.jsx — FarmSense AI v2.0
 * Displays top 5 crop recommendations, govt schemes summary, and analysis stats.
 * No emojis. Premium enterprise layout.
 */
import CropCard from './CropCard';

function fmtINR(n) {
  if (n >= 10000000) return `${(n / 10000000).toFixed(2)} Cr`;
  if (n >= 100000) return `${(n / 100000).toFixed(2)} L`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return `${Math.round(n)}`;
}

const BackIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="15 18 9 12 15 6"/>
  </svg>
);

export default function ResultsPanel({ results, onBack, inputParams }) {
  const {
    recommendations, model_accuracy,
    parameters_analyzed, total_crops_evaluated,
    land_area, budget_per_acre,
  } = results;

  // Collect all unique govt schemes across recommendations
  const allSchemes = [];
  const seenSchemes = new Set();
  recommendations.forEach((rec) => {
    rec.govt_schemes?.forEach((s) => {
      if (!seenSchemes.has(s.name)) {
        seenSchemes.add(s.name);
        allSchemes.push(s);
      }
    });
  });

  // Best revenue crop
  const bestRev = recommendations.reduce(
    (best, r) => (r.potential_revenue > best.potential_revenue ? r : best),
    recommendations[0]
  );

  return (
    <div className="flex flex-col gap-8 animate-fade-in">
      {/* ── Top bar: title + back button */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{
            fontFamily: 'Space Grotesk, sans-serif', fontWeight: 700, fontSize: 26,
            background: 'linear-gradient(135deg, #5dbf55, #7dd977, #d4a843)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text', margin: '0 0 4px',
          }}>
            Top Crop Recommendations
          </h2>
          <p style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: 'var(--text-muted)', margin: 0, letterSpacing: '0.04em' }}>
            {recommendations.length} crops selected from {total_crops_evaluated} evaluated · Score threshold applied (min 50/100 all metrics)
          </p>
        </div>
        <button
          id="back-btn"
          onClick={onBack}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          aria-label="Go back to input form"
        >
          <BackIcon />
          Recalculate
        </button>
      </div>

      {/* ── Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr) repeat(2, 1fr)', gap: 12 }}>
        {[
          { label: 'Parameters Analyzed', value: parameters_analyzed, sub: 'soil + climate + context', color: 'var(--accent-bright)' },
          { label: 'Crops Evaluated',     value: total_crops_evaluated,  sub: 'Indian crop database',    color: 'var(--accent-blue)' },
          { label: 'Model Accuracy',      value: `${model_accuracy}%`,   sub: 'random forest classifier', color: 'var(--accent-gold)' },
          { label: 'Best Est. Revenue',   value: `INR ${fmtINR(bestRev.potential_revenue)}`, sub: `per cycle · ${bestRev.crop}`, color: '#7dd977' },
        ].map(({ label, value, sub, color }) => (
          <div key={label} style={{
            padding: '16px 18px', borderRadius: 14,
            background: 'rgba(8,18,7,0.7)',
            border: '1px solid var(--border-subtle)',
            display: 'flex', flexDirection: 'column', gap: 4,
          }}>
            <div style={{ fontFamily: 'Space Mono, monospace', fontWeight: 700, fontSize: 20, color }}>
              {value}
            </div>
            <div style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 12, color: 'var(--text-primary)' }}>
              {label}
            </div>
            <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 11, color: 'var(--text-muted)' }}>
              {sub}
            </div>
          </div>
        ))}
      </div>

      {/* ── Score legend */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: 16,
        padding: '14px 18px', borderRadius: 14,
        background: 'rgba(0,0,0,0.25)',
        border: '1px solid var(--border-subtle)',
        alignItems: 'center',
      }}>
        <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginRight: 4 }}>
          Scoring:
        </span>
        {[
          { label: 'Soil Fit (45%)',      color: '#5dbf55', desc: 'ML model confidence from your soil profile' },
          { label: 'Market Score (35%)',  color: '#4a9fbe', desc: 'Price index + demand + export potential' },
          { label: 'Profit Index (20%)', color: '#d4a843', desc: 'Yield potential × market value blend' },
        ].map(({ label, color, desc }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
            <div>
              <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 11, fontWeight: 700, color }}>
                {label}
              </span>
              <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 11, color: 'var(--text-muted)', marginLeft: 4 }}>
                — {desc}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* ── Analysis context */}
      {inputParams && (
        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 8,
          padding: '12px 16px', borderRadius: 12,
          background: 'rgba(74,153,67,0.04)',
          border: '1px solid var(--border-subtle)',
        }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif', fontWeight: 600, marginRight: 4 }}>
            Analyzed for:
          </span>
          {[
            land_area && `${land_area} acres`,
            budget_per_acre && `Budget INR ${fmtINR(budget_per_acre)}/acre`,
            inputParams?.season && `${inputParams.season} season`,
            inputParams?.irrigation && `${inputParams.irrigation} irrigation`,
            inputParams?.location && inputParams.location,
          ].filter(Boolean).map((item) => (
            <span key={item} style={{
              padding: '3px 10px', borderRadius: 20,
              background: 'rgba(74,153,67,0.08)',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'Space Mono, monospace', fontSize: 11,
              color: 'var(--text-secondary)',
            }}>
              {item}
            </span>
          ))}
        </div>
      )}

      {/* ── Crop Cards */}
      <div className="flex flex-col gap-5">
        {recommendations.map((rec, idx) => (
          <CropCard key={rec.crop} rec={rec} delay={idx * 100} />
        ))}
      </div>

      {/* ── Government Schemes Summary */}
      {allSchemes.length > 0 && (
        <div style={{
          borderRadius: 18,
          border: '1px solid rgba(74,153,67,0.2)',
          overflow: 'hidden',
        }}>
          <div style={{
            padding: '14px 20px',
            background: 'rgba(74,153,67,0.07)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <div style={{
              width: 24, height: 24, borderRadius: 6,
              background: 'rgba(74,153,67,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--accent-bright)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h3 style={{
              fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 14,
              color: 'var(--accent-bright)', margin: 0,
            }}>
              Available Government Schemes
            </h3>
            <span style={{
              marginLeft: 'auto',
              fontFamily: 'Space Mono, monospace', fontSize: 11,
              color: 'var(--text-muted)',
            }}>
              {allSchemes.length} schemes identified
            </span>
          </div>

          <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            {allSchemes.slice(0, 6).map((scheme) => (
              <div key={scheme.name} className="scheme-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 5 }}>
                  <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>
                    {scheme.name}
                  </span>
                  <span style={{
                    fontFamily: 'Space Mono, monospace', fontSize: 10,
                    color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)',
                    padding: '2px 8px', borderRadius: 10, flexShrink: 0, marginLeft: 10,
                  }}>
                    {scheme.body}
                  </span>
                </div>
                <p style={{ margin: 0, fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {scheme.benefit}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Disclaimer */}
      <div style={{
        padding: '14px 18px', borderRadius: 12,
        background: 'rgba(20,35,19,0.5)',
        border: '1px solid var(--border-subtle)',
      }}>
        <p style={{
          margin: 0,
          fontFamily: 'Space Mono, monospace', fontSize: 11,
          color: 'var(--text-muted)', lineHeight: 1.65,
        }}>
          Recommendations are based on ML analysis of soil parameters and historical crop data.
          Revenue projections use estimated yields and Agmarknet 2024-25 price data.
          Always consult a local agronomist and current market conditions before making final decisions.
          Government scheme eligibility is subject to state-specific rules and annual budget allocations.
        </p>
      </div>
    </div>
  );
}
