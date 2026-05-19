# 🌿 FarmSense AI — Intelligent Crop Recommendation System

> **AI-powered crop advisory for Indian farmers.** Enter your soil parameters and location, and get the top 3 crop recommendations ranked by soil suitability, market demand, and profitability — all powered by a trained Random Forest ML model.

---

## 🌾 Features

- **ML-Powered Predictions** — Random Forest Classifier trained on 2,200 soil samples across 22 crop types
- **Live Weather Integration** — Auto-fills temperature, humidity, and rainfall from Open-Meteo (no API key needed)
- **Market Scoring** — Static market scores for all 22 crops based on MSP, demand, and export potential
- **Dynamic Reasoning** — Human-readable explanation for every recommendation based on actual soil values
- **Animated Gauge Charts** — Real SVG circular gauges for Soil Fit, Market Score, and Profit Index
- **Drag-and-Drop Upload** — UI for soil report uploads (AI extraction roadmap)
- **Dark-theme UI** — Professional dark green design with Syne + Space Mono fonts

---

## 📁 Project Structure

```
farmsense-ai/
├── backend/
│   ├── main.py           # FastAPI app (POST /predict, GET /weather)
│   ├── model.py          # ML model: train / save / load / predict
│   ├── market_data.py    # Static market scores for 22 crops
│   ├── requirements.txt
│   └── data/
│       └── crop_data.csv     ← You must place the dataset here
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── index.css
│   │   └── components/
│   │       ├── InputForm.jsx
│   │       ├── UploadReport.jsx
│   │       ├── ResultsPanel.jsx
│   │       ├── CropCard.jsx
│   │       └── GaugeChart.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
└── run.sh
```

---

## 🚀 Setup Instructions

### 1. Dataset (Required)

Download the **Crop Recommendation Dataset** from Kaggle:
> https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

Rename the file to `crop_data.csv` and place it at:
```
backend/data/crop_data.csv
```

The CSV must have these columns:
```
N, P, K, temperature, humidity, ph, rainfall, label
```

---

### 2. Backend (Python + FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

On first run, the model will train automatically (~10 seconds) and save `model.pkl`.  
Subsequent runs load the pre-trained model instantly.

---

### 3. Frontend (React + Vite + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

Open your browser at **http://localhost:5173**

---

### 4. Quick Start (Both at once — Linux/macOS)

```bash
chmod +x run.sh
./run.sh
```

> **Windows users:** Run the backend and frontend commands in two separate terminals.

---

## 🧠 How the Scoring Works

Each recommended crop is scored using a weighted formula:

```
overall_score = (fit_score × 0.45) + (market_score × 0.35) + (profit_index × 0.20)
```

| Score         | Source                                           |
|---------------|--------------------------------------------------|
| `fit_score`   | ML model confidence × 100                       |
| `market_score`| Weighted avg: MSP (40%) + demand (40%) + export (20%) |
| `profit_index`| Blend of fit_score and market_score              |

---

## 🌤 Weather Auto-Fill

Click **"🌤 Auto-fill"** after entering your city name. This calls:
1. Open-Meteo Geocoding API → converts city name to lat/lon
2. Open-Meteo Forecast API → fetches current temperature, humidity, and estimates annual rainfall

No API key required. Works for any city worldwide.

---

## 📸 Screenshots

> *(Add screenshots here after running the app)*

| Input Screen | Results Screen |
|---|---|
| `[screenshot_input.png]` | `[screenshot_results.png]` |

---

## 🛠 Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | React 18, Vite 5, Tailwind CSS 3  |
| Backend   | Python 3.10+, FastAPI, Uvicorn    |
| ML Model  | scikit-learn RandomForestClassifier |
| Weather   | Open-Meteo API (free, no key)     |
| Fonts     | Google Fonts: Syne + Space Mono   |

---

## 📋 Crops Supported (22)

rice, wheat, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

---

## ⚠️ Disclaimer

Recommendations are for educational and advisory purposes. Always consult a certified agronomist and check local mandi prices before making crop decisions.

---

*FarmSense AI — Built for Indian Agriculture*
