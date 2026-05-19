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
import requests

from model import load_or_train, predict_top_n, get_model_accuracy, generate_reason
from market_data import get_market_score, MARKET_SCORES, DEMAND_SCORES

INDIA_COUNTRY_CODE = "IN"

INDIAN_LOCATION_ALIASES = {
    "bangalore": "Bengaluru",
    "banglore": "Bengaluru",
    "mysore": "Mysuru",
    "mangalore": "Mangaluru",
    "bellary": "Ballari",
    "bellari": "Ballari",
    "bellaria": "Ballari",
    "baroda": "Vadodara",
    "calcutta": "Kolkata",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "gurgaon": "Gurugram",
}

POPULAR_INDIAN_LOCATIONS = [
    {"name": "Bengaluru", "admin1": "Karnataka", "admin2": "Bengaluru Urban", "latitude": 12.97194, "longitude": 77.59369, "population": 8495492, "priority": 0, "aliases": ["bangalore", "banglore", "bengaluru"]},
    {"name": "Bengaluru Rural", "admin1": "Karnataka", "admin2": "Bengaluru Rural", "latitude": 13.22567, "longitude": 77.57501, "population": 990923, "priority": 5, "aliases": ["bangalore rural", "bengaluru rural"]},
    {"name": "Bengaluru Urban", "admin1": "Karnataka", "admin2": "Bengaluru Urban", "latitude": 12.97056, "longitude": 77.59456, "population": 9621551, "priority": 5, "aliases": ["bangalore urban", "bengaluru urban"]},
    {"name": "Bangarapet", "admin1": "Karnataka", "admin2": "Kolar", "latitude": 12.99116, "longitude": 78.17804, "population": 43500, "priority": 10, "aliases": ["bangarapet"]},
    {"name": "Ballari", "admin1": "Karnataka", "admin2": "Ballari", "latitude": 15.14205, "longitude": 76.92398, "population": 410445, "aliases": ["bellary", "bellari", "bellaria", "ballari"]},
    {"name": "Belagavi", "admin1": "Karnataka", "admin2": "Belagavi", "latitude": 15.85212, "longitude": 74.50447, "population": 488157, "aliases": ["belgaum", "belagavi"]},
    {"name": "Belur", "admin1": "Karnataka", "admin2": "Hassan", "latitude": 13.16231, "longitude": 75.86754, "population": 20319, "aliases": ["belur"]},
    {"name": "Bellampalli", "admin1": "Telangana", "admin2": "Mancherial", "latitude": 19.05577, "longitude": 79.49300, "population": 55841, "aliases": ["bellampalli"]},
    {"name": "Beldanga", "admin1": "West Bengal", "admin2": "Murshidabad", "latitude": 23.93428, "longitude": 88.26018, "population": 29634, "aliases": ["beldanga"]},
    {"name": "Mumbai", "admin1": "Maharashtra", "admin2": "Mumbai", "latitude": 19.07283, "longitude": 72.88261, "population": 12691836, "aliases": ["bombay", "mumbai"]},
    {"name": "Delhi", "admin1": "National Capital Territory of Delhi", "admin2": "Delhi", "latitude": 28.65195, "longitude": 77.23149, "population": 10927986, "aliases": ["delhi", "new delhi"]},
    {"name": "Pune", "admin1": "Maharashtra", "admin2": "Pune", "latitude": 18.51957, "longitude": 73.85535, "population": 3124458, "aliases": ["pune"]},
    {"name": "Hyderabad", "admin1": "Telangana", "admin2": "Hyderabad", "latitude": 17.38405, "longitude": 78.45636, "population": 6809970, "aliases": ["hyderabad"]},
    {"name": "Chennai", "admin1": "Tamil Nadu", "admin2": "Chennai", "latitude": 13.08784, "longitude": 80.27847, "population": 4328063, "aliases": ["madras", "chennai"]},
    {"name": "Kolkata", "admin1": "West Bengal", "admin2": "Kolkata", "latitude": 22.56263, "longitude": 88.36304, "population": 4631392, "aliases": ["calcutta", "kolkata"]},
    {"name": "Ahmedabad", "admin1": "Gujarat", "admin2": "Ahmedabad", "latitude": 23.02579, "longitude": 72.58727, "population": 6357693, "aliases": ["ahmedabad"]},
    {"name": "Jaipur", "admin1": "Rajasthan", "admin2": "Jaipur", "latitude": 26.91962, "longitude": 75.78781, "population": 2711758, "aliases": ["jaipur"]},
    {"name": "Lucknow", "admin1": "Uttar Pradesh", "admin2": "Lucknow", "latitude": 26.83928, "longitude": 80.92313, "population": 2472011, "aliases": ["lucknow"]},
    {"name": "Kanpur", "admin1": "Uttar Pradesh", "admin2": "Kanpur Nagar", "latitude": 26.46523, "longitude": 80.34975, "population": 2823249, "aliases": ["kanpur"]},
    {"name": "Nagpur", "admin1": "Maharashtra", "admin2": "Nagpur", "latitude": 21.14631, "longitude": 79.08491, "population": 2228018, "aliases": ["nagpur"]},
    {"name": "Indore", "admin1": "Madhya Pradesh", "admin2": "Indore", "latitude": 22.71792, "longitude": 75.83330, "population": 1837041, "aliases": ["indore"]},
    {"name": "Bhopal", "admin1": "Madhya Pradesh", "admin2": "Bhopal", "latitude": 23.25469, "longitude": 77.40289, "population": 1599914, "aliases": ["bhopal"]},
    {"name": "Patna", "admin1": "Bihar", "admin2": "Patna", "latitude": 25.59408, "longitude": 85.13563, "population": 1599920, "aliases": ["patna"]},
    {"name": "Ludhiana", "admin1": "Punjab", "admin2": "Ludhiana", "latitude": 30.91204, "longitude": 75.85379, "population": 1545368, "aliases": ["ludhiana"]},
    {"name": "Nashik", "admin1": "Maharashtra", "admin2": "Nashik", "latitude": 19.99745, "longitude": 73.78980, "population": 1289497, "aliases": ["nashik", "nasik"]},
    {"name": "Surat", "admin1": "Gujarat", "admin2": "Surat", "latitude": 21.19594, "longitude": 72.83023, "population": 4467797, "aliases": ["surat"]},
    {"name": "Vadodara", "admin1": "Gujarat", "admin2": "Vadodara", "latitude": 22.29941, "longitude": 73.20812, "population": 1409476, "aliases": ["vadodara", "baroda"]},
    {"name": "Chandigarh", "admin1": "Chandigarh", "admin2": "Chandigarh", "latitude": 30.73629, "longitude": 76.78840, "population": 960787, "aliases": ["chandigarh"]},
    {"name": "Mysuru", "admin1": "Karnataka", "admin2": "Mysuru", "latitude": 12.29791, "longitude": 76.63925, "population": 868313, "aliases": ["mysore", "mysuru"]},
    {"name": "Mangaluru", "admin1": "Karnataka", "admin2": "Dakshina Kannada", "latitude": 12.91723, "longitude": 74.85603, "population": 417387, "aliases": ["mangalore", "mangaluru"]},
    {"name": "Coimbatore", "admin1": "Tamil Nadu", "admin2": "Coimbatore", "latitude": 11.00555, "longitude": 76.96612, "population": 959823, "aliases": ["coimbatore"]},
    {"name": "Kochi", "admin1": "Kerala", "admin2": "Ernakulam", "latitude": 9.93988, "longitude": 76.26022, "population": 604696, "aliases": ["kochi", "cochin"]},
    {"name": "Guwahati", "admin1": "Assam", "admin2": "Kamrup Metropolitan", "latitude": 26.18440, "longitude": 91.74580, "population": 899094, "aliases": ["guwahati"]},
    {"name": "Bhubaneswar", "admin1": "Odisha", "admin2": "Khordha", "latitude": 20.27241, "longitude": 85.83385, "population": 762243, "aliases": ["bhubaneswar"]},
    {"name": "Ranchi", "admin1": "Jharkhand", "admin2": "Ranchi", "latitude": 23.34316, "longitude": 85.30940, "population": 846454, "aliases": ["ranchi"]},
    {"name": "Banda", "admin1": "Uttar Pradesh", "admin2": "Banda", "latitude": 25.47534, "longitude": 80.33580, "population": 160473, "aliases": ["banda"]},
    {"name": "Bankura", "admin1": "West Bengal", "admin2": "Bankura", "latitude": 23.23241, "longitude": 87.07160, "population": 137386, "aliases": ["bankura"]},
    {"name": "Banswara", "admin1": "Rajasthan", "admin2": "Banswara", "latitude": 23.54614, "longitude": 74.43490, "population": 99969, "aliases": ["banswara"]},
    {"name": "Banaskantha", "admin1": "Gujarat", "admin2": "Banaskantha", "latitude": 24.17243, "longitude": 72.43458, "population": 3120506, "aliases": ["banaskantha", "palanpur"]},
]

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


def _canonical_indian_location(query: str) -> str:
    normalized = " ".join(query.strip().lower().split())
    return INDIAN_LOCATION_ALIASES.get(normalized, query.strip())


def _location_display(result: dict) -> str:
    parts = [
        result.get("name"),
        result.get("admin2"),
        result.get("admin1"),
        result.get("country"),
    ]
    seen = set()
    clean_parts = []
    for part in parts:
        if not part:
            continue
        key = str(part).strip().lower()
        if key and key not in seen:
            seen.add(key)
            clean_parts.append(str(part).strip())
    return ", ".join(clean_parts)


def _local_indian_locations(query: str) -> list[dict]:
    normalized = " ".join(query.strip().lower().split())
    if len(normalized) < 2:
        return []

    matches = []
    for item in POPULAR_INDIAN_LOCATIONS:
        names = [item["name"].lower(), *[alias.lower() for alias in item.get("aliases", [])]]
        starts = any(name.startswith(normalized) for name in names)
        contains = any(normalized in name for name in names)
        if starts or contains:
            result = {
                **item,
                "country": "India",
                "country_code": INDIA_COUNTRY_CODE,
                "id": f"local-{item['name'].lower()}",
            }
            score = 0 if starts else 1
            matches.append((score, int(item.get("priority", 50)), -int(item.get("population") or 0), result))

    return [item for _, _, _, item in sorted(matches, key=lambda row: (row[0], row[1], row[2], row[3]["name"]))[:4]]


def _search_indian_locations(query: str, count: int = 4) -> list[dict]:
    """
    Search Open-Meteo geocoding but keep only Indian locations.
    Open-Meteo uses current official names for several Indian cities, so a
    small alias map handles common older spellings such as Bangalore/Bellary.
    """
    query = query.strip()
    if len(query) < 2:
        return []

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    search_terms = [query]
    canonical = _canonical_indian_location(query)
    if canonical.lower() != query.lower():
        search_terms.insert(0, canonical)

    matches = []
    seen_keys = set()

    for result in _local_indian_locations(query):
        key = (result.get("name", "").lower(), result.get("admin1", "").lower())
        seen_keys.add(key)
        matches.append(result)

    for term in search_terms:
        params = {
            "name": term,
            "count": max(count * 3, 10),
            "language": "en",
            "format": "json",
            "countryCode": INDIA_COUNTRY_CODE,
        }
        resp = requests.get(geo_url, params=params, timeout=10)
        resp.raise_for_status()

        for result in resp.json().get("results") or []:
            if result.get("country_code") != INDIA_COUNTRY_CODE:
                continue
            key = (result.get("name", "").lower(), result.get("admin1", "").lower())
            if key in seen_keys:
                continue
            seen_keys.add(key)
            matches.append(result)

    preferred = canonical.lower()
    matches.sort(
        key=lambda item: (
            0 if str(item.get("id", "")).startswith("local-") else 1,
            0 if item.get("name", "").lower() == preferred else 1,
            int(item.get("priority", 100)),
            -int(item.get("population") or 0),
            item.get("name", ""),
        )
    )
    return matches[:count]


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
        total_crops_evaluated=len(MARKET_SCORES),
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
    """Returns current market price reference data for all supported crops."""
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


@app.get("/locations")
async def get_location_suggestions(query: str = Query(..., min_length=2, description="Indian city or district search text")):
    """Returns up to 4 Indian location suggestions for weather auto-fill."""
    try:
        matches = _search_indian_locations(query, count=4)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Location suggestion request failed: {e}")

    return {
        "suggestions": [
            {
                "name": item.get("name", ""),
                "display_name": _location_display(item),
                "admin1": item.get("admin1", ""),
                "admin2": item.get("admin2", ""),
                "country": item.get("country", "India"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
            }
            for item in matches
        ]
    }


# ─── /weather endpoint ────────────────────────────────────────────────────────

@app.get("/weather")
async def get_weather(location: str = Query(..., description="City or district name")):
    """
    Fetches real-time weather from Open-Meteo (no API key required).
    Returns values ready to auto-fill the frontend climate inputs.
    """
    try:
        results = _search_indian_locations(location, count=1)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding request failed: {e}")

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Indian location '{location}' not found. Try a nearby Indian city or district.",
        )

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    resolved_location = _location_display(results[0])

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
        "location": resolved_location,
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
        "total_crops": len(MARKET_SCORES),
    }


# ─── Dev entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
