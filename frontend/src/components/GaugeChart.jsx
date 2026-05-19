/**
 * GaugeChart.jsx — FarmSense AI
 * A real circular SVG gauge chart that animates from 0 to the given value.
 *
 * Props:
 *   value       {number}  0–100
 *   label       {string}  Label below gauge
 *   color       {string}  Stroke color (hex)
 *   size        {number}  SVG width/height in px (default 110)
 */
import { useEffect, useRef, useState } from 'react';

export default function GaugeChart({ value = 0, label = '', color = '#6abf5e', size = 110 }) {
  const [displayed, setDisplayed] = useState(0);
  const animRef = useRef(null);

  // Animate from 0 → value on mount / value change
  useEffect(() => {
    const duration = 1000; // ms
    const start = performance.now();
    const from = 0;
    const to = Math.max(0, Math.min(100, value));

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(Math.round(from + (to - from) * eased));
      if (progress < 1) animRef.current = requestAnimationFrame(tick);
    }

    animRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animRef.current);
  }, [value]);

  // SVG arc math
  const cx = size / 2;
  const cy = size / 2;
  const r = (size / 2) - 10;
  const strokeWidth = 8;

  // Full circle circumference
  const circumference = 2 * Math.PI * r;

  // We use 270° arc (from 135° to 405°, i.e., bottom-left to bottom-right)
  const arcLength = circumference * 0.75; // 270/360
  const filledLength = arcLength * (displayed / 100);
  const gapLength = circumference - arcLength;

  // Arc starts at 135° (bottom-left), goes clockwise
  const startAngle = 135 * (Math.PI / 180);
  const startX = cx + r * Math.cos(startAngle);
  const startY = cy + r * Math.sin(startAngle);

  // Determine color based on value
  const getValueColor = (v) => {
    if (v >= 75) return color;
    if (v >= 50) return '#f5c842';
    return '#e05252';
  };

  const valueColor = getValueColor(displayed);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-label={`${label}: ${displayed}%`}
      >
        {/* Background track (270° arc) */}
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="#1e3b1a"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${gapLength}`}
          strokeDashoffset={-circumference * (135 / 360) * -1}
          strokeLinecap="round"
          style={{
            transform: `rotate(${135}deg)`,
            transformOrigin: `${cx}px ${cy}px`,
          }}
        />

        {/* Filled arc */}
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={valueColor}
          strokeWidth={strokeWidth}
          strokeDasharray={`${filledLength} ${circumference - filledLength}`}
          strokeLinecap="round"
          style={{
            transform: `rotate(${135}deg)`,
            transformOrigin: `${cx}px ${cy}px`,
            filter: `drop-shadow(0 0 6px ${valueColor}66)`,
            transition: 'stroke 0.3s ease',
          }}
        />

        {/* Center value text */}
        <text
          x={cx}
          y={cy - 4}
          textAnchor="middle"
          fontSize={size * 0.2}
          fontWeight="700"
          fontFamily="Space Mono, monospace"
          fill={valueColor}
        >
          {displayed}
        </text>
        <text
          x={cx}
          y={cy + size * 0.14}
          textAnchor="middle"
          fontSize={size * 0.1}
          fontFamily="Space Mono, monospace"
          fill="#7aab72"
        >
          /100
        </text>
      </svg>

      {/* Label */}
      <span
        className="text-xs font-mono text-farm-textmuted text-center leading-tight"
        style={{ fontFamily: "'Space Mono', monospace", fontSize: '11px' }}
      >
        {label}
      </span>
    </div>
  );
}
