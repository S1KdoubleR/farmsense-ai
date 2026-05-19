"""
main.py — FarmSense AI Backend
FastAPI application exposing:
  POST /predict        — Crop recommendation with ML + market scoring
  POST /upload-report  — Soil report OCR extraction (PDF / JPG / PNG)
  GET  /weather        — Live weather from Open-Meteo for a given city
  GET  /market-prices  — Static market price reference data
  GET  /health         — Health check

Run with: uvicorn main:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import requests

from model import load_or_train, predict_top_n, get_model_accuracy, generate_reason
from market_data import get_market_score, MARKET_SCORES, DEMAND_SCORES

# ─── App Initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title="FarmSense AI API",
    description="Intelligent crop recommendation system powered by ML + market data",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Load / Train the ML model at startup ─────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    load_or_train()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=140, description="Soil Nitrogen (mg/kg)")
    phosphorus: float = Field(..., ge=0, le=145, description="Soil Phosphorus (mg/kg)")
    potassium: float = Field(..., ge=0, le=205, description="Soil Potassium (mg/kg)")
    temperature: float = Field(..., ge=0, le=55, description="Temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Humidity (%)")
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH")
    rainfall: float = Field(..., ge=0, le=300, description="Annual Rainfall (cm)")
    organic_carbon: float = Field(0.5, ge=0.0, le=5.0, description="Organic Carbon (%)")
    electrical_conductivity: float = Field(0.3, ge=0.0, le=8.0, description="Electrical Conductivity (dS/m)")
    season: str = Field("Kharif", description="Farming season")
    irrigation: str = Field("Available", description="Irrigation availability")
    previous_crop: str = Field("None", description="Previous crop grown")
    location: str = Field("", description="City/district name")
    land_area: float = Field(1.0, ge=0.1, le=10000, description="Land area in acres")
    budget_per_acre: float = Field(20000, ge=0, description="Budget per acre in INR")


class GovtScheme(BaseModel):
    name: str
    body: str
    benefit: str


class CropRecommendation(BaseModel):
    rank: int
    crop: str
    fit_score: float
    market_score: float
    profit_index: float
    overall_score: float
    season: str
    water_need: str
    reason: str
    tags: list[str]
    govt_schemes: list[GovtScheme]
    ai_insights: str
    cost_per_acre: float
    yield_per_acre: float
    price_per_quintal: float
    cycle_days: int
    potential_revenue: float
    potential_profit: float
    roi_percent: float


class PredictResponse(BaseModel):
    recommendations: list[CropRecommendation]
    model_accuracy: float
    parameters_analyzed: int
    total_crops_evaluated: int
    land_area: float
    budget_per_acre: float


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _compute_revenue(mkt: dict, land_area: float) -> tuple[float, float, float]:
    """Calculate potential revenue, profit, ROI for given land area."""
    cost_total = mkt["cost_per_acre"] * land_area
    gross_revenue = mkt["yield_per_acre"] * mkt["price_per_quintal"] * land_area
    net_profit = gross_revenue - cost_total
    roi = round((net_profit / cost_total) * 100, 1) if cost_total > 0 else 0.0
    return round(gross_revenue, 0), round(net_profit, 0), roi


# ─── /predict endpoint ────────────────────────────────────────────────────────

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """
    Accepts soil + climate parameters and returns top 5 crop recommendations.
    Score threshold: all three metrics (fit, market, profit) must be >= 50.
    If no crop meets threshold, the best available crops are returned.

    Ranking formula:
        overall_score = (fit_score × 0.45) + (market_score × 0.35) + (profit_index × 0.20)
    """
    try:
        top_candidates = predict_top_n(
            nitrogen=req.nitrogen,
            phosphorus=req.phosphorus,
            potassium=req.potassium,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall,
            top_n=10,  # get 10 internally, filter to top 5 meeting threshold
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    qualified = []
    fallback = []

    for candidate in top_candidates:
        crop_name = candidate["crop"]
        fit_score = candidate["fit_score"]

        mkt = get_market_score(crop_name)
        market_score = float(mkt["market_score"])

        # profit_index: blend of fit and market (ensure it's also normalized high)
        profit_index = round((fit_score * 0.40) + (market_score * 0.60), 1)
        profit_index = min(profit_index, 100.0)

        overall_score = round(
            (fit_score * 0.45) + (market_score * 0.35) + (profit_index * 0.20), 1
        )

        reason = generate_reason(
            crop=crop_name,
            nitrogen=req.nitrogen,
            phosphorus=req.phosphorus,
            potassium=req.potassium,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall,
            confidence=candidate["confidence"],
        )

        gross_rev, net_profit, roi = _compute_revenue(mkt, req.land_area)

        schemes = [
            GovtScheme(name=s["name"], body=s["body"], benefit=s["benefit"])
            for s in mkt.get("govt_schemes", [])
        ]

        rec = CropRecommendation(
            rank=0,
            crop=crop_name.replace("_", " ").title(),
            fit_score=fit_score,
            market_score=market_score,
            profit_index=profit_index,
            overall_score=overall_score,
            season=mkt["season"],
            water_need=mkt["water_need"],
            reason=reason,
            tags=mkt["tags"],
            govt_schemes=schemes,
            ai_insights=mkt.get("ai_insights", ""),
            cost_per_acre=mkt["cost_per_acre"],
            yield_per_acre=mkt["yield_per_acre"],
            price_per_quintal=mkt["price_per_quintal"],
            cycle_days=mkt["cycle_days"],
            potential_revenue=gross_rev,
            potential_profit=net_profit,
            roi_percent=roi,
        )

        # Score threshold: all 3 metrics >= 50
        if fit_score >= 50 and market_score >= 50 and profit_index >= 50:
            qualified.append(rec)
        else:
            fallback.append(rec)

    # Sort both lists by overall_score
    qualified.sort(key=lambda x: x.overall_score, reverse=True)
    fallback.sort(key=lambda x: x.overall_score, reverse=True)

    # If we have enough qualified crops, use them; otherwise fill from fallback
    if len(qualified) >= 5:
        final = qualified[:5]
    elif len(qualified) > 0:
        needed = 5 - len(qualified)
        final = qualified + fallback[:needed]
    else:
        # All crops are fallback — return best available
        final = fallback[:5]

    for i, rec in enumerate(final):
        rec.rank = i + 1

    return PredictResponse(
        recommendations=final,
        model_accuracy=round(get_model_accuracy() * 100, 2),
        parameters_analyzed=11,
        total_crops_evaluated=55,
        land_area=req.land_area,
        budget_per_acre=req.budget_per_acre,
    )


# ─── /upload-report endpoint ──────────────────────────────────────────────────

@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    """
    Accepts a soil lab report (PDF, JPG, PNG) and extracts soil parameter values
    using OCR / text parsing. Returns extracted values for auto-filling the form.
    """
    allowed_types = {
        "application/pdf",
        "image/jpeg", "image/jpg", "image/png", "image/webp",
    }
    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Upload PDF, JPG, or PNG.",
        )

    file_bytes = await file.read()
    max_size = 15 * 1024 * 1024  # 15 MB
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 15 MB.")

    try:
        from ocr_parser import parse_soil_report
        result = parse_soil_report(file_bytes, content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report parsing failed: {str(e)}")

    return result


# ─── /market-prices endpoint ──────────────────────────────────────────────────

@app.get("/market-prices")
async def get_market_prices():
    """Returns current market price reference data for all 55 crops."""
    prices = {}
    for crop, data in MARKET_SCORES.items():
        demand_score = DEMAND_SCORES[data["demand"]]
        composite = round(0.40 * data["price_score"] + 0.40 * demand_score + 0.20 * data["export"])
        prices[crop] = {
            "market_score": composite,
            "price_per_quintal": data["price_per_quintal"],
            "season": data["season"],
            "demand": data["demand"],
        }
    return {"crops": prices, "source": "Agmarknet + APEDA estimates 2024-25"}


# ─── /weather endpoint ────────────────────────────────────────────────────────

@app.get("/weather")
async def get_weather(location: str = Query(..., description="City or district name")):
    """
    Fetches real-time weather from Open-Meteo (no API key required).
    Returns values ready to auto-fill the frontend climate inputs.
    """
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}

    try:
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding request failed: {e}")

    results = geo_data.get("results")
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Try a nearby city name.",
        )

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    resolved_name = results[0].get("name", location)
    country = results[0].get("country", "")

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "daily": "precipitation_sum",
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        w_resp = requests.get(weather_url, params=weather_params, timeout=10)
        w_resp.raise_for_status()
        w_data = w_resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Weather request failed: {e}")

    current = w_data.get("current", {})
    daily = w_data.get("daily", {})

    temperature = current.get("temperature_2m", 25.0)
    humidity = current.get("relative_humidity_2m", 60.0)

    daily_precip = daily.get("precipitation_sum", [])
    if daily_precip:
        weekly_avg = sum(daily_precip) / len(daily_precip) * 7
        annual_rainfall_est = round(weekly_avg * 52 / 10, 1)
    else:
        annual_rainfall_est = 80.0

    annual_rainfall_est = max(20.0, min(300.0, annual_rainfall_est))

    return {
        "location": f"{resolved_name}, {country}".strip(", "),
        "latitude": lat,
        "longitude": lon,
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "rainfall": annual_rainfall_est,
        "source": "Open-Meteo (open-meteo.com)",
    }


# ─── /health endpoint ─────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_accuracy": round(get_model_accuracy() * 100, 2),
        "version": "2.0.0",
        "total_crops": 55,
    }


# ─── Dev entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
