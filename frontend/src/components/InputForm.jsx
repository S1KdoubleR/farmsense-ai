/**
 * InputForm.jsx — FarmSense AI v2.0
 * Premium enterprise input form.
 * - Every parameter has a slider + number input (fully synced)
 * - New parameters: Organic Carbon, Electrical Conductivity
 * - Farm economics: Land Area, Budget per Acre
 * - Real-time weather auto-fill
 * - Tab: Manual Entry | Upload Soil Report
 */
import { useState } from 'react';
import { getWeather } from '../api';
import UploadReport from './UploadReport';

// ── SVG Icons ──────────────────────────────────────────────────────────────
const Icon = {
  Soil: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  Climate: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
    </svg>
  ),
  Farm: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>
  ),
  Economics: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
    </svg>
  ),
  Goals: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  Location: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
    </svg>
  ),
  Upload: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  Edit: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  ),
};

// ── Parameter definitions ──────────────────────────────────────────────────
const SOIL_PARAMS = [
  { key: 'nitrogen',    label: 'Nitrogen (N)',          unit: 'mg/kg', min: 0,   max: 140, step: 1,   default: 60,  desc: 'Available soil nitrogen' },
  { key: 'phosphorus',  label: 'Phosphorus (P)',        unit: 'mg/kg', min: 0,   max: 145, step: 1,   default: 40,  desc: 'Available soil phosphorus' },
  { key: 'potassium',   label: 'Potassium (K)',         unit: 'mg/kg', min: 0,   max: 205, step: 1,   default: 50,  desc: 'Available soil potassium' },
  { key: 'ph',          label: 'Soil pH',               unit: 'pH',    min: 3.0, max: 10.0,step: 0.1, default: 6.5, desc: 'Soil acidity/alkalinity' },
  { key: 'organic_carbon', label: 'Organic Carbon',    unit: '%',     min: 0.0, max: 5.0, step: 0.1, default: 0.5, desc: 'Soil organic carbon content' },
  { key: 'electrical_conductivity', label: 'Elect. Conductivity', unit: 'dS/m', min: 0.0, max: 8.0, step: 0.1, default: 0.3, desc: 'Soil salinity indicator' },
];

const CLIMATE_PARAMS = [
  { key: 'temperature', label: 'Temperature',           unit: '°C',   min: 5,   max: 50,  step: 0.5, default: 26,  desc: 'Mean seasonal temperature' },
  { key: 'humidity',    label: 'Relative Humidity',    unit: '%',    min: 10,  max: 100, step: 1,   default: 65,  desc: 'Average humidity' },
  { key: 'rainfall',    label: 'Annual Rainfall',      unit: 'cm',   min: 20,  max: 300, step: 5,   default: 120, desc: 'Annual precipitation' },
];

const INITIAL = {
  nitrogen: 60, phosphorus: 40, potassium: 50, ph: 6.5,
  organic_carbon: 0.5, electrical_conductivity: 0.3,
  temperature: 26, humidity: 65, rainfall: 120,
  season: 'Kharif', irrigation: 'Available', previous_crop: 'None',
  location: '',
  land_area: 2,
  budget_per_acre: 25000,
};

function fillPct(v, min, max) { return ((v - min) / (max - min)) * 100; }

// ── Dual Slider + Number Input Row ─────────────────────────────────────────
function ParamRow({ def, value, onChange }) {
  const pct = fillPct(value, def.min, def.max);

  const handleNumber = (e) => {
    const v = parseFloat(e.target.value);
    if (!isNaN(v)) {
      onChange(def.key, Math.max(def.min, Math.min(def.max, parseFloat(v.toFixed(1)))));
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {/* Label row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <label htmlFor={`slider-${def.key}`} style={{
            fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13,
            color: 'var(--text-primary)',
          }}>
            {def.label}
          </label>
          {def.desc && (
            <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>
              {def.desc}
            </span>
          )}
        </div>
        {/* Numeric input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <input
            type="number"
            className="param-number-input"
            value={value}
            min={def.min}
            max={def.max}
            step={def.step}
            onChange={handleNumber}
            id={`input-${def.key}`}
            aria-label={`${def.label} numeric input`}
          />
          <span style={{
            fontSize: 11, color: 'var(--text-muted)',
            fontFamily: 'Space Mono, monospace',
            minWidth: 36,
          }}>{def.unit}</span>
        </div>
      </div>

      {/* Slider */}
      <input
        id={`slider-${def.key}`}
        type="range"
        min={def.min}
        max={def.max}
        step={def.step}
        value={value}
        onChange={(e) => onChange(def.key, parseFloat(e.target.value))}
        style={{
          background: `linear-gradient(to right, var(--accent-primary) 0%, var(--accent-bright) ${pct}%, #1a3318 ${pct}%, #1a3318 100%)`,
          width: '100%',
        }}
        aria-label={`${def.label} slider`}
      />

      {/* Min/max labels */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>
          {def.min} {def.unit}
        </span>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>
          {def.max} {def.unit}
        </span>
      </div>
    </div>
  );
}

// ── Section wrapper ────────────────────────────────────────────────────────
function Section({ title, icon: IconComp, children }) {
  return (
    <div className="section-card">
      <h3 style={{
        display: 'flex', alignItems: 'center', gap: 8,
        fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 12,
        color: 'var(--accent-bright)',
        textTransform: 'uppercase', letterSpacing: '0.08em',
        margin: '0 0 20px',
      }}>
        <span style={{ color: 'var(--accent-primary)' }}>
          {IconComp && <IconComp />}
        </span>
        {title}
      </h3>
      {children}
    </div>
  );
}

// ── Dropdown ───────────────────────────────────────────────────────────────
function Dropdown({ id, label, value, onChange, options }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{
        fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 12,
        color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em',
      }}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>
        ))}
      </select>
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────
export default function InputForm({ onSubmit, loading }) {
  const [activeTab, setActiveTab] = useState('manual');
  const [values, setValues] = useState(INITIAL);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherMsg, setWeatherMsg] = useState({ text: '', type: '' }); // type: 'success' | 'error'
  const [weatherData, setWeatherData] = useState(null);
  const [optimizations, setOptimizations] = useState({
    profit: true, demand: true, soilHealth: true, water: true,
  });

  const set = (key, val) => setValues((v) => ({ ...v, [key]: val }));

  // Called by UploadReport when OCR extracts values
  const handleExtracted = (extracted) => {
    setValues((v) => ({
      ...v,
      ...(extracted.nitrogen    != null ? { nitrogen: extracted.nitrogen }       : {}),
      ...(extracted.phosphorus  != null ? { phosphorus: extracted.phosphorus }   : {}),
      ...(extracted.potassium   != null ? { potassium: extracted.potassium }     : {}),
      ...(extracted.ph          != null ? { ph: extracted.ph }                   : {}),
      ...(extracted.organic_carbon != null ? { organic_carbon: extracted.organic_carbon } : {}),
    }));
    setActiveTab('manual'); // switch to manual after extraction so user can review
  };

  const handleWeatherFill = async () => {
    if (!values.location.trim()) {
      setWeatherMsg({ text: 'Please enter a city or district name first.', type: 'error' });
      return;
    }
    setWeatherMsg({ text: '', type: '' });
    setWeatherLoading(true);
    try {
      const data = await getWeather(values.location);
      setWeatherData(data);
      setValues((v) => ({
        ...v,
        temperature: Math.min(50, Math.max(5, data.temperature)),
        humidity:    Math.min(100, Math.max(10, data.humidity)),
        rainfall:    Math.min(300, Math.max(20, data.rainfall)),
      }));
      setWeatherMsg({ text: `Weather data loaded for ${data.location}`, type: 'success' });
    } catch (err) {
      setWeatherMsg({ text: err.message, type: 'error' });
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleSubmit = () => {
    onSubmit({
      nitrogen:                values.nitrogen,
      phosphorus:              values.phosphorus,
      potassium:               values.potassium,
      temperature:             values.temperature,
      humidity:                values.humidity,
      ph:                      values.ph,
      rainfall:                values.rainfall,
      organic_carbon:          values.organic_carbon,
      electrical_conductivity: values.electrical_conductivity,
      season:                  values.season,
      irrigation:              values.irrigation,
      previous_crop:           values.previous_crop,
      location:                values.location,
      land_area:               values.land_area,
      budget_per_acre:         values.budget_per_acre,
    });
  };

  return (
    <div className="flex flex-col gap-6 animate-fade-in">
      {/* ── Tab Bar */}
      <div className="tab-bar">
        {[
          { id: 'manual', label: 'Manual Entry',   iconComp: Icon.Edit },
          { id: 'upload', label: 'Upload Soil Report', iconComp: Icon.Upload },
        ].map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab-item ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            id={`tab-${tab.id}`}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <tab.iconComp />
              {tab.label}
            </span>
          </button>
        ))}
      </div>

      {/* ── Upload Tab */}
      {activeTab === 'upload' && (
        <UploadReport onValuesExtracted={handleExtracted} />
      )}

      {/* ── Manual Entry Tab */}
      {activeTab === 'manual' && (
        <div className="flex flex-col gap-5">
          {/* Soil Parameters */}
          <Section title="Soil Parameters" icon={Icon.Soil}>
            <div className="flex flex-col gap-6">
              {SOIL_PARAMS.map((def) => (
                <ParamRow
                  key={def.key}
                  def={def}
                  value={values[def.key]}
                  onChange={set}
                />
              ))}
            </div>
          </Section>

          {/* Climate Parameters */}
          <Section title="Climate & Weather" icon={Icon.Climate}>
            {/* Location + Weather Auto-fill */}
            <div style={{ marginBottom: 20 }}>
              <label style={{
                display: 'block',
                fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13,
                color: 'var(--text-primary)', marginBottom: 8,
              }}>
                Location (for weather auto-fill)
              </label>
              <div style={{ display: 'flex', gap: 8 }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <span style={{
                    position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }}>
                    <Icon.Location />
                  </span>
                  <input
                    id="location-input"
                    type="text"
                    className="text-input"
                    style={{ paddingLeft: 34 }}
                    placeholder="e.g. Nashik, Pune, Indore, Ludhiana..."
                    value={values.location}
                    onChange={(e) => set('location', e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleWeatherFill()}
                    aria-label="Location city name"
                  />
                </div>
                <button
                  id="weather-autofill-btn"
                  onClick={handleWeatherFill}
                  disabled={weatherLoading}
                  className="btn-secondary"
                  style={{ whiteSpace: 'nowrap', cursor: weatherLoading ? 'wait' : 'pointer' }}
                  aria-label="Auto-fill weather from location"
                >
                  {weatherLoading ? 'Loading...' : 'Fetch Weather'}
                </button>
              </div>

              {/* Status messages */}
              {weatherMsg.text && (
                <p style={{
                  marginTop: 8,
                  fontSize: 12,
                  fontFamily: 'Space Mono, monospace',
                  color: weatherMsg.type === 'success' ? 'var(--accent-bright)' : 'var(--red-error)',
                }}>
                  {weatherMsg.text}
                </p>
              )}

              {/* Weather card */}
              {weatherData && (
                <div style={{
                  marginTop: 12, display: 'flex', gap: 12,
                  background: 'rgba(74,153,67,0.05)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 12, padding: '12px 16px',
                }}>
                  {[
                    { label: 'Temperature', value: `${weatherData.temperature}°C` },
                    { label: 'Humidity',    value: `${weatherData.humidity}%` },
                    { label: 'Est. Rainfall', value: `${weatherData.rainfall} cm/yr` },
                  ].map((item) => (
                    <div key={item.label} style={{ flex: 1, textAlign: 'center' }}>
                      <div style={{ fontSize: 16, fontWeight: 700, fontFamily: 'Space Mono, monospace', color: 'var(--accent-bright)' }}>
                        {item.value}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif', marginTop: 2 }}>
                        {item.label}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-col gap-6">
              {CLIMATE_PARAMS.map((def) => (
                <ParamRow
                  key={def.key}
                  def={def}
                  value={values[def.key]}
                  onChange={set}
                />
              ))}
            </div>
          </Section>

          {/* Farm Context */}
          <Section title="Farm Context" icon={Icon.Farm}>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Dropdown
                id="select-season"
                label="Farming Season"
                value={values.season}
                onChange={(v) => set('season', v)}
                options={['Kharif', 'Rabi', 'Zaid', 'Annual']}
              />
              <Dropdown
                id="select-irrigation"
                label="Irrigation"
                value={values.irrigation}
                onChange={(v) => set('irrigation', v)}
                options={['Available', 'Limited', 'Rain-fed only']}
              />
              <Dropdown
                id="select-previous-crop"
                label="Previous Crop"
                value={values.previous_crop}
                onChange={(v) => set('previous_crop', v)}
                options={['None', 'Rice', 'Wheat', 'Cotton', 'Maize', 'Pulse', 'Vegetable', 'Sugarcane', 'Oilseed', 'Fallow']}
              />
            </div>
          </Section>

          {/* Farm Economics */}
          <Section title="Farm Economics" icon={Icon.Economics}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Land Area */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
                    Land Area
                    <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)' }}>Total farm acreage</span>
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <input
                      type="number"
                      className="param-number-input"
                      value={values.land_area}
                      min={0.1} max={10000} step={0.5}
                      onChange={(e) => {
                        const v = parseFloat(e.target.value);
                        if (!isNaN(v)) set('land_area', Math.max(0.1, v));
                      }}
                      id="input-land-area"
                      aria-label="Land area in acres"
                    />
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace', minWidth: 36 }}>acres</span>
                  </div>
                </div>
                <input
                  type="range" min={0.5} max={100} step={0.5}
                  value={Math.min(values.land_area, 100)}
                  onChange={(e) => set('land_area', parseFloat(e.target.value))}
                  style={{
                    background: `linear-gradient(to right, var(--accent-primary) 0%, var(--accent-bright) ${fillPct(Math.min(values.land_area, 100), 0.5, 100)}%, #1a3318 ${fillPct(Math.min(values.land_area, 100), 0.5, 100)}%, #1a3318 100%)`,
                    width: '100%',
                  }}
                  aria-label="Land area slider"
                />
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>0.5 acres</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>100+ acres</span>
                </div>
              </div>

              {/* Budget per Acre */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13, color: 'var(--text-primary)' }}>
                    Budget per Acre
                    <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)' }}>Max input cost</span>
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <input
                      type="number"
                      className="param-number-input"
                      value={values.budget_per_acre}
                      min={0} max={500000} step={1000}
                      onChange={(e) => {
                        const v = parseFloat(e.target.value);
                        if (!isNaN(v)) set('budget_per_acre', Math.max(0, v));
                      }}
                      id="input-budget"
                      aria-label="Budget per acre in INR"
                      style={{ width: 90 }}
                    />
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace', minWidth: 36 }}>INR</span>
                  </div>
                </div>
                <input
                  type="range" min={0} max={150000} step={1000}
                  value={Math.min(values.budget_per_acre, 150000)}
                  onChange={(e) => set('budget_per_acre', parseFloat(e.target.value))}
                  style={{
                    background: `linear-gradient(to right, #d4a843 0%, #e8c43b ${fillPct(Math.min(values.budget_per_acre, 150000), 0, 150000)}%, #1a3318 ${fillPct(Math.min(values.budget_per_acre, 150000), 0, 150000)}%, #1a3318 100%)`,
                    width: '100%',
                  }}
                  aria-label="Budget slider"
                />
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>INR 0</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'Space Mono, monospace' }}>INR 1.5L+</span>
                </div>
              </div>
            </div>
          </Section>

          {/* Optimization Goals */}
          <Section title="Optimization Goals" icon={Icon.Goals}>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { key: 'profit',     label: 'Max Profit',       desc: 'Revenue optimization' },
                { key: 'demand',     label: 'Market Demand',    desc: 'High-demand crops' },
                { key: 'soilHealth', label: 'Soil Health',      desc: 'Sustainable farming' },
                { key: 'water',      label: 'Water Efficiency', desc: 'Low water usage' },
              ].map(({ key, label, desc }) => {
                const active = optimizations[key];
                return (
                  <label
                    key={key}
                    htmlFor={`opt-${key}`}
                    style={{
                      display: 'flex', flexDirection: 'column', gap: 8,
                      padding: '12px 14px', borderRadius: 12, cursor: 'pointer',
                      background: active ? 'rgba(74,153,67,0.1)' : 'rgba(255,255,255,0.02)',
                      border: `1px solid ${active ? 'rgba(74,153,67,0.3)' : 'var(--border-subtle)'}`,
                      transition: 'all 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{
                        fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13,
                        color: active ? 'var(--accent-bright)' : 'var(--text-muted)',
                      }}>{label}</span>
                      <div style={{
                        width: 16, height: 16, borderRadius: 4, flexShrink: 0,
                        background: active ? 'var(--accent-primary)' : 'transparent',
                        border: `2px solid ${active ? 'var(--accent-primary)' : 'var(--text-muted)'}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transition: 'all 0.2s',
                      }}>
                        {active && (
                          <svg width="9" height="9" viewBox="0 0 12 12" fill="none">
                            <polyline points="2 6 5 9 10 3" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        )}
                      </div>
                    </div>
                    <span style={{
                      fontSize: 11, color: 'var(--text-muted)',
                      fontFamily: 'Inter, sans-serif',
                    }}>{desc}</span>
                    <input
                      id={`opt-${key}`}
                      type="checkbox"
                      checked={active}
                      onChange={() => setOptimizations((o) => ({ ...o, [key]: !o[key] }))}
                      style={{ display: 'none' }}
                    />
                  </label>
                );
              })}
            </div>
          </Section>

          {/* Submit CTA */}
          <button
            id="find-crops-btn"
            className="btn-primary w-full"
            onClick={handleSubmit}
            disabled={loading}
            style={{
              padding: '18px', fontSize: '16px',
              opacity: loading ? 0.7 : 1,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            }}
            aria-label="Analyze soil and find best crops"
          >
            {loading ? (
              <>
                <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" strokeWidth="3" opacity="0.25"/>
                  <path d="M4 12a8 8 0 018-8" strokeWidth="3" strokeLinecap="round"/>
                </svg>
                Analyzing Soil Profile...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
                Analyze & Find Best Crops
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
