/**
 * UploadReport.jsx — FarmSense AI v2.0
 * Functional soil report upload with OCR extraction.
 * Supports PDF, JPG, PNG. Calls /upload-report API.
 * Auto-populates form values on successful extraction.
 */
import { useState, useRef } from 'react';
import { uploadSoilReport } from '../api';

const UploadIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)' }}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-bright)' }}>
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const SpinnerIcon = () => (
  <svg className="animate-spin" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{ color: 'var(--accent-bright)' }}>
    <circle cx="12" cy="12" r="10" strokeWidth="2" opacity="0.2"/>
    <path d="M4 12a8 8 0 018-8" strokeWidth="2.5" strokeLinecap="round"/>
  </svg>
);

export default function UploadReport({ onValuesExtracted }) {
  const [file, setFile]           = useState(null);
  const [dragging, setDragging]   = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult]       = useState(null); // OCR result
  const [error, setError]         = useState('');
  const inputRef = useRef(null);

  const ALLOWED = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
  const ALLOWED_EXT = ['.pdf', '.jpg', '.jpeg', '.png'];

  const handleFile = async (f) => {
    if (!f) return;
    if (!ALLOWED.includes(f.type)) {
      setError(`Unsupported format. Please upload ${ALLOWED_EXT.join(', ')} files.`);
      return;
    }
    if (f.size > 15 * 1024 * 1024) {
      setError('File is too large. Maximum size is 15 MB.');
      return;
    }
    setFile(f);
    setError('');
    setResult(null);

    // Auto-upload and extract
    setUploading(true);
    try {
      const data = await uploadSoilReport(f);
      setResult(data);
    } catch (err) {
      setError(`Extraction failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleApply = () => {
    if (result?.extracted && onValuesExtracted) {
      onValuesExtracted(result.extracted);
    }
  };

  const reset = (e) => {
    e?.stopPropagation();
    setFile(null);
    setResult(null);
    setError('');
    if (inputRef.current) inputRef.current.value = '';
  };

  const confidenceColor = { high: 'var(--accent-bright)', medium: 'var(--accent-gold)', low: 'var(--red-error)' };

  return (
    <div className="flex flex-col gap-5 animate-fade-in">
      {/* Drop Zone */}
      <div
        className={`upload-zone ${dragging ? 'dragging' : ''}`}
        style={{
          padding: '48px 24px',
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', gap: 16, minHeight: 240,
          borderColor: dragging ? 'var(--accent-primary)' : undefined,
        }}
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        role="button" tabIndex={0}
        aria-label="Upload soil report file"
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
          id="soil-report-upload"
        />

        <div style={{
          width: 72, height: 72, borderRadius: 18,
          background: 'rgba(74,153,67,0.08)',
          border: '1px solid var(--border-subtle)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {uploading ? <SpinnerIcon /> : file && result ? <CheckIcon /> : <UploadIcon />}
        </div>

        {uploading ? (
          <>
            <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 15, color: 'var(--text-primary)', margin: 0 }}>
              Extracting soil values...
            </p>
            <p style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
              Running OCR analysis on {file?.name}
            </p>
          </>
        ) : file ? (
          <>
            <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 15, color: 'var(--accent-bright)', margin: 0 }}>
              {file.name}
            </p>
            <p style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
              {(file.size / 1024).toFixed(1)} KB · {file.type}
            </p>
            <button
              style={{ fontSize: 12, color: 'var(--red-error)', fontFamily: 'Inter, sans-serif', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
              onClick={reset}
            >
              Remove file
            </button>
          </>
        ) : (
          <>
            <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 16, color: 'var(--text-primary)', margin: 0, textAlign: 'center' }}>
              Drop your soil lab report here
            </p>
            <p style={{ fontFamily: 'Space Mono, monospace', fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
              PDF, JPG or PNG — Maximum 15 MB
            </p>
            <button
              style={{
                marginTop: 4,
                padding: '8px 20px', borderRadius: 8,
                background: 'rgba(74,153,67,0.1)',
                border: '1px solid var(--border-mid)',
                color: 'var(--accent-bright)',
                fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13,
                cursor: 'pointer',
              }}
              onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
            >
              Browse Files
            </button>
          </>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '12px 16px', borderRadius: 10,
          background: 'var(--red-error-bg)',
          border: '1px solid rgba(192,57,43,0.3)',
          color: 'var(--red-error)',
          fontFamily: 'Space Mono, monospace', fontSize: 12,
        }}>
          {error}
        </div>
      )}

      {/* Extraction Results */}
      {result && !uploading && (
        <div style={{
          borderRadius: 14,
          border: `1px solid ${result.confidence === 'high' ? 'rgba(74,153,67,0.3)' : result.confidence === 'medium' ? 'rgba(212,168,67,0.3)' : 'rgba(192,57,43,0.3)'}`,
          background: 'rgba(0,0,0,0.2)',
          overflow: 'hidden',
        }}>
          {/* Header */}
          <div style={{
            padding: '14px 18px',
            background: 'rgba(74,153,67,0.05)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: confidenceColor[result.confidence],
              boxShadow: `0 0 8px ${confidenceColor[result.confidence]}`,
            }} />
            <span style={{
              fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 13,
              color: confidenceColor[result.confidence],
            }}>
              {result.confidence === 'high' ? 'High' : result.confidence === 'medium' ? 'Medium' : 'Low'} Confidence Extraction
            </span>
          </div>

          <div style={{ padding: '16px 18px' }}>
            <p style={{
              fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'var(--text-secondary)',
              margin: '0 0 14px',
            }}>
              {result.message}
            </p>

            {/* Extracted values table */}
            {result.extracted && Object.keys(result.extracted).length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                {Object.entries(result.extracted).map(([key, val]) => (
                  <div key={key} className="stat-row">
                    <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 13, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                      {key.replace('_', ' ')}
                    </span>
                    <span style={{ fontFamily: 'Space Mono, monospace', fontSize: 13, color: 'var(--accent-bright)', fontWeight: 700 }}>
                      {val}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Apply button */}
            {result.extracted && Object.keys(result.extracted).length > 0 && (
              <button
                className="btn-primary"
                onClick={handleApply}
                style={{ marginTop: 16, width: '100%', padding: '12px' }}
                aria-label="Apply extracted values to input form"
              >
                Apply Values to Form
              </button>
            )}
          </div>
        </div>
      )}

      {/* Supported Formats */}
      <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
        {['PDF', 'JPG', 'PNG'].map((fmt) => (
          <div key={fmt} style={{
            padding: '5px 14px', borderRadius: 20,
            background: 'rgba(30,50,28,0.5)',
            color: 'var(--text-muted)',
            fontFamily: 'Space Mono, monospace', fontSize: 11,
            border: '1px solid var(--border-subtle)',
            letterSpacing: '0.06em',
          }}>
            {fmt}
          </div>
        ))}
      </div>

      {/* Note */}
      <div style={{
        padding: '12px 16px', borderRadius: 12,
        background: 'rgba(212,168,67,0.05)',
        border: '1px solid rgba(212,168,67,0.2)',
      }}>
        <p style={{ margin: 0, fontFamily: 'Space Mono, monospace', fontSize: 11, color: 'var(--accent-gold)', lineHeight: 1.6 }}>
          Extraction accuracy depends on report clarity. Scanned reports with handwritten values may need manual correction.
          After applying, values are editable in Manual Entry tab.
        </p>
      </div>
    </div>
  );
}
