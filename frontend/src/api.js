/**
 * api.js — FarmSense AI v2.0
 * Centralized API calls to the FastAPI backend.
 */

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

/**
 * POST /predict
 * Send soil + climate + farm parameters for top 5 crop recommendations.
 */
export async function predictCrops(params) {
  const res = await fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * GET /weather?location={city}
 * Fetch current weather from Open-Meteo for a given city name.
 */
export async function getWeather(location) {
  const res = await fetch(
    `${BASE}/weather?location=${encodeURIComponent(location)}`
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * POST /upload-report
 * Upload a soil report file (PDF/JPG/PNG) for OCR extraction.
 * Returns extracted N/P/K/pH values.
 */
export async function uploadSoilReport(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/upload-report`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * GET /market-prices
 * Returns market price reference data for all 55 crops.
 */
export async function getMarketPrices() {
  const res = await fetch(`${BASE}/market-prices`);
  if (!res.ok) throw new Error("Could not fetch market prices");
  return res.json();
}

/**
 * GET /health
 * Health check — also returns model accuracy.
 */
export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error("Backend not reachable");
  return res.json();
}
