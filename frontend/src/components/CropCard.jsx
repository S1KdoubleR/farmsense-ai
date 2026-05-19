/**
 * CropCard.jsx — FarmSense AI v2.0
 * Premium crop recommendation card with 3-tab view:
 *   Overview | AI Insights | Economics & Revenue
 * No emojis. SVG icons. Score bars. Revenue display.
 */
import { useState } from 'react';
import GaugeChart from './GaugeChart';

// ── Score Bar ───────────────────────────────────────────────────────────────
function ScoreBar({ value, color, label }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
          {label}
        </span>
        <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, fontWeight: 700, color }}>
          {value}<span style={{ fontSize: 10, color: 'var(--text-muted)', marginLeft: 2 }}>/100</span>
        </span>
      </div>
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${value}%`, background: color }}
        />
      </div>
    </div>
  );
}

// ── Water Level Indicator ────────────────────────────────────────────────────
function WaterLevel({ level }) {
  const filled = { High: 3, Medium: 2, Low: 1 }[level] || 1;
  return (
    <div style={{ display: 'flex', gap: 3, alignItems: 'center' }}>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{
          width: 6, height: 12, borderRadius: 3,
          background: i <= filled ? '#4a9fbe' : 'rgba(74,159,190,0.15)',
          transition: 'background 0.3s',
        }} />
      ))}
      <span style={{ marginLeft: 4, fontSize: 12, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>{level}</span>
    </div>
  );
}

function fmtINR(n) {
  if (n >= 10000000) return `${(n / 10000000).toFixed(2)} Cr`;
  if (n >= 100000) return `${(n / 100000).toFixed(2)} L`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return `${Math.round(n)}`;
}

export default function CropCard({ rec, delay = 0 }) {
  const [activeTab, setActiveTab] = useState('overview');
  const isTop = rec.rank === 1;

  const TABS = [
    { id: 'overview',   label: 'Overview' },
    { id: 'insights',   label: 'AI Insights' },
    { id: 'economics',  label: 'Economics' },
  ];

  // Crop initial badge color
  const initials = rec.crop.slice(0, 2).toUpperCase();
  const hue = rec.crop.charCodeAt(0) * 37 % 360;

  return (
    <div
      className="animate-slide-up"
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'both',
        position: 'relative',
        borderRadius: 20,
        padding: isTop ? '0' : '0',
        background: isTop
          ? 'linear-gradient(135deg, rgba(74,153,67,0.09) 0%, rgba(17,34,16,0.97) 60%)'
          : 'rgba(13,24,12,0.97)',
        border: isTop
          ? '1px solid rgba(74,153,67,0.40)'
          : '1px solid rgba(74,153,67,0.12)',
        boxShadow: isTop
          ? '0 12px 48px rgba(0,0,0,0.5), 0 0 0 1px rgba(74,153,67,0.12)'
          : '0 4px 24px rgba(0,0,0,0.4)',
        overflow: 'hidden',
        transition: 'box-shadow 0.3s',
      }}
    >
      {/* Top accent bar for rank 1 */}
      {isTop && (
        <div style={{
          height: 2,
          background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-bright), var(--accent-gold))',
        }} />
      )}

      <div style={{ padding: '22px 24px' }}>
        {/* ── Header row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18 }}>
          {/* Left: rank + crop name */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            {/* Rank badge */}
            <div style={{
              width: 36, height: 36, borderRadius: 10, flexShrink: 0,
              background: isTop ? 'rgba(74,153,67,0.2)' : 'rgba(255,255,255,0.04)',
              border: `1px solid ${isTop ? 'rgba(74,153,67,0.4)' : 'var(--border-subtle)'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'Space Mono, monospace', fontWeight: 700, fontSize: 14,
              color: isTop ? 'var(--accent-bright)' : 'var(--text-muted)',
            }}>
              #{rec.rank}
            </div>

            {/* Crop initial + name */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                background: `hsl(${hue}, 45%, 20%)`,
                border: `1px solid hsl(${hue}, 45%, 30%)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'Space Grotesk, sans-serif', fontWeight: 800, fontSize: 16,
                color: `hsl(${hue}, 60%, 75%)`,
              }}>
                {initials}
              </div>
              <div>
                <h3 style={{
                  margin: 0,
                  fontFamily: 'Space Grotesk, sans-serif', fontWeight: 700, fontSize: 20,
                  color: isTop ? 'var(--accent-bright)' : 'var(--text-primary)',
                }}>
                  {rec.crop}
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
                  <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>
                    {rec.season} Season
                  </span>
                  <span style={{ width: 1, height: 12, background: 'var(--border-subtle)' }} />
                  <WaterLevel level={rec.water_need} />
                </div>
              </div>
            </div>
          </div>

          {/* Right: overall score + TOP PICK badge */}
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            {isTop && (
              <div className="badge-top badge-pulse" style={{ display: 'inline-block', marginBottom: 6 }}>
                Top Pick
              </div>
            )}
            <div style={{
              fontFamily: 'Space Mono, monospace', fontWeight: 700,
              fontSize: 32, color: isTop ? 'var(--accent-bright)' : 'var(--text-primary)',
              lineHeight: 1,
            }}>
              {rec.overall_score}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace', letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: 2 }}>
              Overall Score
            </div>
          </div>
        </div>

        {/* ── Tab bar */}
        <div className="crop-tab-bar" style={{ marginBottom: 20 }}>
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`crop-tab ${activeTab === t.id ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}
              id={`crop-tab-${rec.rank}-${t.id}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* ── Overview Tab */}
        {activeTab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            {/* Score bars */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <ScoreBar value={rec.fit_score}    color="#5dbf55" label="Soil Fit Score" />
              <ScoreBar value={rec.market_score} color="#4a9fbe" label="Market Score" />
              <ScoreBar value={rec.profit_index} color="#d4a843" label="Profit Index" />
            </div>

            {/* Reason */}
            <p style={{
              margin: 0,
              fontFamily: 'Inter, sans-serif', fontSize: 13, lineHeight: 1.65,
              color: 'var(--text-secondary)',
            }}>
              {rec.reason}
            </p>

            {/* Quick stats row */}
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10,
            }}>
              {[
                { label: 'Crop Cycle',   value: `${rec.cycle_days} days` },
                { label: 'Water Need',   value: rec.water_need },
                { label: 'Season',       value: rec.season },
              ].map(({ label, value }) => (
                <div key={label} style={{
                  padding: '10px 12px', borderRadius: 10,
                  background: 'rgba(74,153,67,0.04)',
                  border: '1px solid var(--border-subtle)',
                  textAlign: 'center',
                }}>
                  <div style={{ fontFamily: 'Space Mono, monospace', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>
                    {value}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif', marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {label}
                  </div>
                </div>
              ))}
            </div>

            {/* Tags */}
            {rec.tags?.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {rec.tags.map((tag) => (
                  <span key={tag} className="tag-pill">{tag}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── AI Insights Tab */}
        {activeTab === 'insights' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{
              padding: '14px 16px', borderRadius: 12,
              background: 'rgba(74,153,67,0.05)',
              border: '1px solid var(--border-subtle)',
            }}>
              <p style={{
                margin: 0,
                fontFamily: 'Inter, sans-serif', fontSize: 13.5, lineHeight: 1.75,
                color: 'var(--text-secondary)',
              }}>
                {rec.ai_insights || rec.reason}
              </p>
            </div>

            {/* Score gauges for reference */}
            <div style={{
              display: 'flex', justifyContent: 'space-around', alignItems: 'center',
              padding: '14px', borderRadius: 12,
              background: 'rgba(0,0,0,0.2)',
            }}>
              <GaugeChart value={rec.fit_score}    label="Soil Fit"    color="#5dbf55" size={90} />
              <GaugeChart value={rec.market_score} label="Market"      color="#4a9fbe" size={90} />
              <GaugeChart value={rec.profit_index} label="Profit"      color="#d4a843" size={90} />
            </div>
          </div>
        )}

        {/* ── Economics Tab */}
        {activeTab === 'economics' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Revenue highlight */}
            <div className="revenue-card">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                {[
                  { label: 'Gross Revenue', value: `INR ${fmtINR(rec.potential_revenue)}`, sub: 'per cycle', color: 'var(--accent-bright)' },
                  { label: 'Net Profit',    value: `INR ${fmtINR(rec.potential_profit)}`,  sub: 'after costs', color: rec.potential_profit >= 0 ? '#7dd977' : 'var(--red-error)' },
                  { label: 'ROI',           value: `${rec.roi_percent}%`,                  sub: 'return on investment', color: 'var(--accent-gold)' },
                ].map(({ label, value, sub, color }) => (
                  <div key={label} style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'Space Mono, monospace', fontWeight: 700, fontSize: 16, color }}>
                      {value}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontFamily: 'Inter, sans-serif', marginTop: 4 }}>
                      {label}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>
                      {sub}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Economics breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {[
                { label: 'Cost per Acre',        value: `INR ${fmtINR(rec.cost_per_acre)}` },
                { label: 'Expected Yield',        value: `${rec.yield_per_acre} quintals/acre` },
                { label: 'Market Price',          value: `INR ${fmtINR(rec.price_per_quintal)}/quintal` },
                { label: 'Crop Cycle',            value: `${rec.cycle_days} days` },
              ].map(({ label, value }) => (
                <div key={label} className="stat-row">
                  <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'var(--text-secondary)' }}>{label}</span>
                  <span style={{ fontFamily: 'Space Mono, monospace', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{value}</span>
                </div>
              ))}
            </div>

            {/* Government Schemes */}
            {rec.govt_schemes?.length > 0 && (
              <div>
                <h4 style={{
                  fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 12,
                  color: 'var(--accent-bright)', textTransform: 'uppercase',
                  letterSpacing: '0.08em', margin: '10px 0 10px',
                }}>
                  Available Government Schemes
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {rec.govt_schemes.slice(0, 3).map((scheme) => (
                    <div key={scheme.name} className="scheme-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                        <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>
                          {scheme.name}
                        </span>
                        <span style={{
                          fontFamily: 'Space Mono, monospace', fontSize: 10,
                          color: 'var(--text-muted)',
                          background: 'rgba(255,255,255,0.04)',
                          padding: '2px 8px', borderRadius: 10,
                          flexShrink: 0, marginLeft: 8,
                        }}>
                          {scheme.body}
                        </span>
                      </div>
                      <p style={{ margin: 0, fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        {scheme.benefit}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
