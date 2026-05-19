"""
model.py — FarmSense AI
ML model training, saving, and prediction logic.

Uses scikit-learn Random Forest Classifier trained on the full crop dataset.
Features: N, P, K, temperature, humidity, ph, rainfall (7 numeric features)
Target:   label (crop classes)

On startup:
  - If model.pkl exists → load it
  - If not → train from data/crop_data.csv → save as model.pkl
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "crop_data.csv"
MODEL_PATH = BASE_DIR / "model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"
META_PATH = BASE_DIR / "model_meta.pkl"

# ─── Feature columns (must match CSV column names) ────────────────────────────
FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
LABEL_COL = "label"

# ─── Global references (loaded once at import time) ───────────────────────────
_model: RandomForestClassifier | None = None
_encoder: LabelEncoder | None = None
_model_accuracy: float = 0.0


def _train_and_save() -> tuple[RandomForestClassifier, LabelEncoder, float]:
    """Load CSV, train Random Forest, persist artefacts, return model + encoder + accuracy."""
    if not DATA_PATH.exists():
        print("\n" + "=" * 60)
        print("ERROR: Training dataset not found!")
        print(f"Expected path: {DATA_PATH}")
        print("Please run: python generate_dataset.py")
        print("=" * 60 + "\n")
        sys.exit(1)

    print(f"[model] Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)

    missing = [c for c in FEATURE_COLS + [LABEL_COL] if c not in df.columns]
    if missing:
        print(f"[model] ERROR: Missing columns in CSV: {missing}")
        sys.exit(1)

    print(f"[model] Dataset shape: {df.shape}  |  Classes: {df[LABEL_COL].nunique()}")

    X = df[FEATURE_COLS].values
    y_raw = df[LABEL_COL].values

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("[model] Training Random Forest Classifier ...")
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"[model] Test accuracy: {accuracy * 100:.2f}%")

    joblib.dump(clf, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    joblib.dump({"accuracy": accuracy}, META_PATH)
    print(f"[model] Saved -> {MODEL_PATH}, {ENCODER_PATH}")

    return clf, encoder, accuracy


def load_or_train() -> None:
    """Load pre-trained model from disk; train + save if not present."""
    global _model, _encoder, _model_accuracy

    if MODEL_PATH.exists() and ENCODER_PATH.exists():
        print("[model] Loading pre-trained model from disk ...")
        _model = joblib.load(MODEL_PATH)
        _encoder = joblib.load(ENCODER_PATH)
        meta = joblib.load(META_PATH) if META_PATH.exists() else {"accuracy": 0.0}
        _model_accuracy = meta.get("accuracy", 0.0)
        print(f"[model] Loaded. Accuracy: {_model_accuracy * 100:.2f}%")
    else:
        print("[model] No pre-trained model found — training from scratch ...")
        _model, _encoder, _model_accuracy = _train_and_save()


def get_model_accuracy() -> float:
    """Return the test-set accuracy from the last training run (0.0–1.0)."""
    return _model_accuracy


def predict_top_n(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    top_n: int = 5,
) -> list[dict]:
    """
    Run inference and return the top_n crops with their NORMALIZED fit scores.

    Normalization: raw model probabilities across many classes are often small (e.g. 0.15).
    We normalize so the top candidate maps to a fit_score of 85–95, and lower
    candidates scale proportionally — ensuring all recommended crops score >= 50.

    Returns:
        [{"crop": "cotton", "confidence": 0.91, "fit_score": 88.5}, ...]
        sorted by fit_score descending.
    """
    if _model is None or _encoder is None:
        raise RuntimeError("Model not loaded. Call load_or_train() first.")

    features = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
    proba = _model.predict_proba(features)[0]  # shape: (n_classes,)

    # Get indices of top_n highest probabilities
    top_indices = np.argsort(proba)[::-1][:top_n]

    raw_scores = [float(proba[idx]) for idx in top_indices]
    max_raw = max(raw_scores) if raw_scores else 1.0

    results = []
    for i, idx in enumerate(top_indices):
        crop_name = _encoder.inverse_transform([idx])[0]
        raw_conf = float(proba[idx])

        # Normalize: top candidate → 85–95 range; scale others proportionally
        # Minimum allowed fit_score = 52 (all recommended crops must score ≥ 50)
        normalized = (raw_conf / max_raw) * 55.0 + 40.0  # range: 40–95
        # Ensure minimum 52 for any crop we return
        fit_score = max(52.0, round(normalized, 1))

        results.append({
            "crop": crop_name,
            "confidence": raw_conf,
            "fit_score": fit_score,
        })

    return results


# ─── Optimal soil ranges for supported crops ─────────────────────────────────
OPTIMAL = {
    "rice":        dict(N=(60,100), P=(30,60),  K=(30,60),  temp=(20,30), rain=(100,200), ph=(5.5,7.0)),
    "wheat":       dict(N=(60,120), P=(30,60),  K=(30,60),  temp=(15,25), rain=(50,100),  ph=(6.0,7.5)),
    "maize":       dict(N=(80,120), P=(40,80),  K=(40,80),  temp=(18,27), rain=(50,100),  ph=(5.8,7.0)),
    "chickpea":    dict(N=(20,60),  P=(40,80),  K=(20,50),  temp=(15,25), rain=(25,75),   ph=(6.0,8.0)),
    "kidneybeans": dict(N=(20,60),  P=(50,90),  K=(40,80),  temp=(18,27), rain=(75,125),  ph=(6.0,7.5)),
    "pigeonpeas":  dict(N=(20,50),  P=(40,80),  K=(20,50),  temp=(18,30), rain=(60,150),  ph=(5.5,7.0)),
    "mothbeans":   dict(N=(20,40),  P=(30,60),  K=(20,40),  temp=(25,35), rain=(20,60),   ph=(6.0,8.0)),
    "mungbean":    dict(N=(20,50),  P=(30,70),  K=(20,50),  temp=(20,35), rain=(40,100),  ph=(6.0,7.5)),
    "blackgram":   dict(N=(20,50),  P=(30,70),  K=(20,50),  temp=(20,30), rain=(50,100),  ph=(6.0,7.5)),
    "lentil":      dict(N=(20,50),  P=(40,80),  K=(20,50),  temp=(15,25), rain=(25,75),   ph=(6.0,8.0)),
    "pomegranate": dict(N=(20,60),  P=(20,50),  K=(40,80),  temp=(25,35), rain=(30,80),   ph=(5.5,7.5)),
    "banana":      dict(N=(100,140),P=(50,80),  K=(100,200),temp=(20,30), rain=(100,200), ph=(5.5,7.0)),
    "mango":       dict(N=(20,60),  P=(20,50),  K=(40,80),  temp=(25,35), rain=(75,150),  ph=(5.5,7.5)),
    "grapes":      dict(N=(0,40),   P=(0,50),   K=(50,100), temp=(20,35), rain=(30,90),   ph=(6.0,8.0)),
    "watermelon":  dict(N=(60,100), P=(50,80),  K=(50,100), temp=(25,35), rain=(40,80),   ph=(6.0,7.5)),
    "muskmelon":   dict(N=(60,100), P=(50,80),  K=(50,100), temp=(25,38), rain=(30,70),   ph=(6.0,7.0)),
    "apple":       dict(N=(0,40),   P=(0,40),   K=(40,80),  temp=(10,22), rain=(100,150), ph=(5.5,6.5)),
    "orange":      dict(N=(20,60),  P=(20,50),  K=(40,80),  temp=(15,30), rain=(50,150),  ph=(5.5,7.0)),
    "papaya":      dict(N=(60,100), P=(40,80),  K=(50,100), temp=(20,35), rain=(75,150),  ph=(6.0,7.5)),
    "coconut":     dict(N=(20,60),  P=(20,50),  K=(100,200),temp=(20,35), rain=(100,200), ph=(5.5,7.5)),
    "cotton":      dict(N=(100,140),P=(40,80),  K=(40,80),  temp=(20,35), rain=(60,150),  ph=(6.0,8.0)),
    "jute":        dict(N=(60,100), P=(30,60),  K=(30,60),  temp=(20,35), rain=(150,300), ph=(6.0,7.5)),
    "coffee":      dict(N=(100,140),P=(20,50),  K=(100,200),temp=(15,28), rain=(100,200), ph=(5.0,6.5)),
    "tomato":      dict(N=(40,80),  P=(30,60),  K=(40,80),  temp=(20,30), rain=(40,80),   ph=(6.0,7.0)),
    "potato":      dict(N=(60,100), P=(40,80),  K=(60,120), temp=(15,25), rain=(40,80),   ph=(5.0,6.5)),
    "onion":       dict(N=(50,80),  P=(30,60),  K=(40,80),  temp=(15,25), rain=(35,75),   ph=(6.0,7.5)),
    "garlic":      dict(N=(40,70),  P=(30,60),  K=(40,80),  temp=(12,24), rain=(40,75),   ph=(6.0,8.0)),
    "ginger":      dict(N=(70,120), P=(40,70),  K=(50,90),  temp=(22,32), rain=(120,200), ph=(5.5,6.5)),
    "turmeric":    dict(N=(80,120), P=(40,70),  K=(60,100), temp=(24,32), rain=(120,200), ph=(5.5,7.0)),
    "chilli":      dict(N=(40,80),  P=(30,65),  K=(40,80),  temp=(20,30), rain=(50,100),  ph=(6.0,7.5)),
    "capsicum":    dict(N=(50,90),  P=(35,70),  K=(50,90),  temp=(18,28), rain=(50,90),   ph=(6.0,7.0)),
    "cabbage":     dict(N=(80,130), P=(35,65),  K=(60,100), temp=(15,22), rain=(40,80),   ph=(6.0,7.5)),
    "cauliflower": dict(N=(75,120), P=(35,65),  K=(55,95),  temp=(14,22), rain=(35,75),   ph=(6.0,7.0)),
    "spinach":     dict(N=(90,140), P=(25,55),  K=(50,90),  temp=(12,20), rain=(30,60),   ph=(6.5,7.5)),
    "carrot":      dict(N=(30,60),  P=(35,65),  K=(70,110), temp=(12,20), rain=(30,60),   ph=(6.0,7.0)),
    "radish":      dict(N=(35,65),  P=(30,55),  K=(60,100), temp=(15,22), rain=(30,55),   ph=(6.0,7.5)),
    "sweet_potato":dict(N=(25,55),  P=(40,70),  K=(80,120), temp=(22,30), rain=(60,100),  ph=(5.5,7.0)),
    "sugarcane":   dict(N=(100,140),P=(40,80),  K=(60,100), temp=(25,35), rain=(100,200), ph=(6.0,8.0)),
    "tobacco":     dict(N=(70,110), P=(40,70),  K=(60,100), temp=(22,30), rain=(70,120),  ph=(5.5,7.5)),
    "tea":         dict(N=(80,130), P=(20,40),  K=(30,60),  temp=(18,25), rain=(150,300), ph=(4.5,6.0)),
    "rubber":      dict(N=(60,100), P=(15,35),  K=(25,55),  temp=(25,32), rain=(200,300), ph=(4.5,6.5)),
    "cashew":      dict(N=(40,70),  P=(15,35),  K=(20,50),  temp=(25,35), rain=(80,150),  ph=(5.5,7.0)),
    "strawberry":  dict(N=(30,60),  P=(70,130), K=(80,140), temp=(12,20), rain=(40,80),   ph=(5.5,6.5)),
    "pineapple":   dict(N=(70,110), P=(25,50),  K=(60,100), temp=(24,32), rain=(100,200), ph=(4.5,6.5)),
    "guava":       dict(N=(30,60),  P=(25,55),  K=(35,65),  temp=(24,32), rain=(75,150),  ph=(5.5,7.5)),
    "lemon":       dict(N=(25,55),  P=(20,50),  K=(35,65),  temp=(20,30), rain=(75,150),  ph=(5.5,7.5)),
    "mustard":     dict(N=(50,80),  P=(35,65),  K=(30,60),  temp=(16,24), rain=(25,60),   ph=(6.0,8.0)),
    "sunflower":   dict(N=(45,75),  P=(40,70),  K=(45,75),  temp=(20,28), rain=(35,70),   ph=(6.0,8.0)),
    "soybean":     dict(N=(10,40),  P=(50,90),  K=(35,70),  temp=(22,30), rain=(70,120),  ph=(6.0,7.5)),
    "groundnut":   dict(N=(10,40),  P=(40,80),  K=(35,70),  temp=(24,32), rain=(50,100),  ph=(6.0,8.0)),
    "sesame":      dict(N=(35,65),  P=(30,60),  K=(20,50),  temp=(25,35), rain=(30,60),   ph=(5.5,8.0)),
    "castor":      dict(N=(40,70),  P=(35,65),  K=(30,60),  temp=(24,32), rain=(35,75),   ph=(6.0,8.0)),
    "coriander":   dict(N=(35,65),  P=(25,55),  K=(30,60),  temp=(15,25), rain=(40,80),   ph=(6.5,8.0)),
    "cumin":       dict(N=(30,60),  P=(20,50),  K=(25,55),  temp=(18,26), rain=(20,45),   ph=(6.5,8.0)),
    "cardamom":    dict(N=(55,85),  P=(35,65),  K=(40,70),  temp=(20,28), rain=(180,280), ph=(5.5,7.0)),
    "pepper":      dict(N=(60,90),  P=(30,60),  K=(35,65),  temp=(22,30), rain=(150,250), ph=(5.5,7.0)),
}


def generate_reason(
    crop: str,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    confidence: float,
) -> str:
    """
    Generate a human-readable explanation for why this crop was recommended,
    based on the actual input values vs typical optimal ranges.
    """
    crop_l = crop.lower()
    opt = OPTIMAL.get(crop_l, {})
    reasons = []

    if opt:
        n_lo, n_hi = opt["N"]
        if n_lo <= nitrogen <= n_hi:
            reasons.append(f"nitrogen level ({nitrogen:.0f} mg/kg) is in the optimal range")
        elif nitrogen < n_lo:
            reasons.append(f"nitrogen ({nitrogen:.0f} mg/kg) is manageable with top-dressing supplementation")
        else:
            reasons.append(f"nitrogen ({nitrogen:.0f} mg/kg) is well-suited for high nutrient demand")

        ph_lo, ph_hi = opt["ph"]
        if ph_lo <= ph <= ph_hi:
            reasons.append(f"soil pH ({ph:.1f}) is ideal for this crop")
        else:
            reasons.append(f"soil pH ({ph:.1f}) may need slight amendment for optimal results")

        t_lo, t_hi = opt["temp"]
        if t_lo <= temperature <= t_hi:
            reasons.append(f"temperature ({temperature:.1f}°C) matches ideal growing conditions")
        else:
            reasons.append(f"temperature ({temperature:.1f}°C) is outside ideal window — consider season timing")

        r_lo, r_hi = opt["rain"]
        if r_lo <= rainfall <= r_hi:
            reasons.append(f"annual rainfall ({rainfall:.0f} cm) is well-matched")
        elif rainfall > r_hi:
            reasons.append(f"rainfall ({rainfall:.0f} cm) is abundant — drainage management recommended")
        else:
            reasons.append(f"rainfall ({rainfall:.0f} cm) is lower than ideal — supplemental irrigation can compensate")

    conf_pct = round(confidence * 100)
    if confidence >= 0.30:
        conf_text = f"Strong model fit ({conf_pct}% base probability) across your complete soil-climate profile."
    elif confidence >= 0.15:
        conf_text = f"Good model match ({conf_pct}% base probability) — consider a detailed soil test for precision."
    else:
        conf_text = f"Secondary recommendation based on soil pattern similarity — verify with a local agronomist."

    if reasons:
        joined = "; ".join(reasons[:3]).capitalize() + "."
        return f"{joined} {conf_text}"
    else:
        return f"Based on your soil and climate profile, {crop} is a viable crop choice. {conf_text}"
