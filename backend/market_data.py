"""
market_data.py — FarmSense AI
Market scoring data for all supported crops available in the recommendation system.
Includes: market scores, cost/yield/revenue data, government schemes, and AI insights.
Sources: Agmarknet, APEDA, India Agristat 2023-24, PM-KISAN portal, RKVY guidelines.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Market scores for every crop the ML model can predict.
# price_score      : normalized average mandi price index (0–100)
# demand           : "high" | "medium" | "low"  → maps to 100 / 65 / 35
# export           : export opportunity score (0–100)
# water_need       : qualitative water requirement
# season           : primary growing season label
# cost_per_acre    : estimated input cost (INR/acre)
# yield_per_acre   : expected yield (quintals/acre)
# price_per_quintal: MSP or average mandi price (INR/quintal)
# cycle_days       : crop cycle in days
# ─────────────────────────────────────────────────────────────────────────────

MARKET_SCORES: dict[str, dict] = {
    "rice": {
        "price_score": 72, "demand": "high", "export": 80,
        "water_need": "High", "season": "Kharif",
        "cost_per_acre": 18000, "yield_per_acre": 20, "price_per_quintal": 2183, "cycle_days": 120,
    },
    "wheat": {
        "price_score": 68, "demand": "high", "export": 75,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 14000, "yield_per_acre": 18, "price_per_quintal": 2275, "cycle_days": 120,
    },
    "maize": {
        "price_score": 60, "demand": "high", "export": 65,
        "water_need": "Medium", "season": "Kharif",
        "cost_per_acre": 12000, "yield_per_acre": 22, "price_per_quintal": 2090, "cycle_days": 100,
    },
    "chickpea": {
        "price_score": 78, "demand": "high", "export": 55,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 10000, "yield_per_acre": 8, "price_per_quintal": 5440, "cycle_days": 110,
    },
    "kidneybeans": {
        "price_score": 82, "demand": "medium", "export": 60,
        "water_need": "Medium", "season": "Kharif",
        "cost_per_acre": 12000, "yield_per_acre": 6, "price_per_quintal": 6200, "cycle_days": 90,
    },
    "pigeonpeas": {
        "price_score": 76, "demand": "high", "export": 50,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 9000, "yield_per_acre": 7, "price_per_quintal": 7000, "cycle_days": 150,
    },
    "mothbeans": {
        "price_score": 65, "demand": "medium", "export": 40,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 7000, "yield_per_acre": 5, "price_per_quintal": 5000, "cycle_days": 75,
    },
    "mungbean": {
        "price_score": 74, "demand": "high", "export": 48,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 8000, "yield_per_acre": 5, "price_per_quintal": 7755, "cycle_days": 65,
    },
    "blackgram": {
        "price_score": 71, "demand": "high", "export": 45,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 8500, "yield_per_acre": 5, "price_per_quintal": 6950, "cycle_days": 80,
    },
    "lentil": {
        "price_score": 77, "demand": "medium", "export": 52,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 9000, "yield_per_acre": 6, "price_per_quintal": 6000, "cycle_days": 110,
    },
    "pomegranate": {
        "price_score": 89, "demand": "high", "export": 83,
        "water_need": "Low", "season": "Annual",
        "cost_per_acre": 50000, "yield_per_acre": 40, "price_per_quintal": 8000, "cycle_days": 180,
    },
    "banana": {
        "price_score": 63, "demand": "high", "export": 70,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 40000, "yield_per_acre": 120, "price_per_quintal": 1500, "cycle_days": 365,
    },
    "mango": {
        "price_score": 86, "demand": "high", "export": 88,
        "water_need": "Medium", "season": "Zaid",
        "cost_per_acre": 25000, "yield_per_acre": 50, "price_per_quintal": 5000, "cycle_days": 365,
    },
    "grapes": {
        "price_score": 92, "demand": "high", "export": 90,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 80000, "yield_per_acre": 80, "price_per_quintal": 6000, "cycle_days": 365,
    },
    "watermelon": {
        "price_score": 58, "demand": "medium", "export": 35,
        "water_need": "Medium", "season": "Zaid",
        "cost_per_acre": 20000, "yield_per_acre": 100, "price_per_quintal": 800, "cycle_days": 90,
    },
    "muskmelon": {
        "price_score": 60, "demand": "medium", "export": 30,
        "water_need": "Medium", "season": "Zaid",
        "cost_per_acre": 18000, "yield_per_acre": 80, "price_per_quintal": 1000, "cycle_days": 85,
    },
    "apple": {
        "price_score": 90, "demand": "high", "export": 78,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 60000, "yield_per_acre": 60, "price_per_quintal": 8000, "cycle_days": 365,
    },
    "orange": {
        "price_score": 75, "demand": "high", "export": 72,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 30000, "yield_per_acre": 60, "price_per_quintal": 3500, "cycle_days": 365,
    },
    "papaya": {
        "price_score": 62, "demand": "medium", "export": 55,
        "water_need": "Medium", "season": "Annual",
        "cost_per_acre": 25000, "yield_per_acre": 100, "price_per_quintal": 1200, "cycle_days": 270,
    },
    "coconut": {
        "price_score": 70, "demand": "high", "export": 76,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 20000, "yield_per_acre": 4000, "price_per_quintal": 150, "cycle_days": 365,
    },
    "cotton": {
        "price_score": 91, "demand": "high", "export": 88,
        "water_need": "High", "season": "Kharif",
        "cost_per_acre": 25000, "yield_per_acre": 8, "price_per_quintal": 6620, "cycle_days": 180,
    },
    "jute": {
        "price_score": 55, "demand": "medium", "export": 62,
        "water_need": "High", "season": "Kharif",
        "cost_per_acre": 12000, "yield_per_acre": 20, "price_per_quintal": 4500, "cycle_days": 120,
    },
    "coffee": {
        "price_score": 95, "demand": "high", "export": 95,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 35000, "yield_per_acre": 8, "price_per_quintal": 25000, "cycle_days": 365,
    },
    # New crops
    "tomato": {
        "price_score": 70, "demand": "high", "export": 55,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 35000, "yield_per_acre": 80, "price_per_quintal": 1500, "cycle_days": 90,
    },
    "potato": {
        "price_score": 65, "demand": "high", "export": 50,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 30000, "yield_per_acre": 100, "price_per_quintal": 1200, "cycle_days": 90,
    },
    "onion": {
        "price_score": 72, "demand": "high", "export": 70,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 25000, "yield_per_acre": 80, "price_per_quintal": 2000, "cycle_days": 120,
    },
    "garlic": {
        "price_score": 83, "demand": "high", "export": 65,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 30000, "yield_per_acre": 30, "price_per_quintal": 8000, "cycle_days": 150,
    },
    "ginger": {
        "price_score": 85, "demand": "high", "export": 70,
        "water_need": "High", "season": "Kharif",
        "cost_per_acre": 60000, "yield_per_acre": 50, "price_per_quintal": 8000, "cycle_days": 270,
    },
    "turmeric": {
        "price_score": 80, "demand": "high", "export": 80,
        "water_need": "High", "season": "Kharif",
        "cost_per_acre": 40000, "yield_per_acre": 30, "price_per_quintal": 7000, "cycle_days": 270,
    },
    "chilli": {
        "price_score": 78, "demand": "high", "export": 75,
        "water_need": "Medium", "season": "Kharif",
        "cost_per_acre": 30000, "yield_per_acre": 15, "price_per_quintal": 8000, "cycle_days": 150,
    },
    "capsicum": {
        "price_score": 75, "demand": "medium", "export": 60,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 40000, "yield_per_acre": 40, "price_per_quintal": 5000, "cycle_days": 120,
    },
    "cabbage": {
        "price_score": 55, "demand": "medium", "export": 30,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 20000, "yield_per_acre": 100, "price_per_quintal": 600, "cycle_days": 90,
    },
    "cauliflower": {
        "price_score": 60, "demand": "medium", "export": 35,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 22000, "yield_per_acre": 80, "price_per_quintal": 900, "cycle_days": 90,
    },
    "spinach": {
        "price_score": 58, "demand": "medium", "export": 25,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 15000, "yield_per_acre": 50, "price_per_quintal": 1500, "cycle_days": 45,
    },
    "carrot": {
        "price_score": 62, "demand": "medium", "export": 40,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 18000, "yield_per_acre": 80, "price_per_quintal": 1200, "cycle_days": 90,
    },
    "radish": {
        "price_score": 50, "demand": "medium", "export": 20,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 12000, "yield_per_acre": 60, "price_per_quintal": 800, "cycle_days": 45,
    },
    "sweet_potato": {
        "price_score": 56, "demand": "medium", "export": 30,
        "water_need": "Medium", "season": "Kharif",
        "cost_per_acre": 15000, "yield_per_acre": 60, "price_per_quintal": 1400, "cycle_days": 120,
    },
    "sugarcane": {
        "price_score": 65, "demand": "high", "export": 60,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 35000, "yield_per_acre": 300, "price_per_quintal": 350, "cycle_days": 365,
    },
    "tobacco": {
        "price_score": 70, "demand": "medium", "export": 75,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 30000, "yield_per_acre": 10, "price_per_quintal": 15000, "cycle_days": 180,
    },
    "tea": {
        "price_score": 82, "demand": "high", "export": 85,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 45000, "yield_per_acre": 8, "price_per_quintal": 20000, "cycle_days": 365,
    },
    "rubber": {
        "price_score": 75, "demand": "high", "export": 70,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 30000, "yield_per_acre": 6, "price_per_quintal": 18000, "cycle_days": 365,
    },
    "cashew": {
        "price_score": 88, "demand": "high", "export": 85,
        "water_need": "Low", "season": "Annual",
        "cost_per_acre": 20000, "yield_per_acre": 8, "price_per_quintal": 15000, "cycle_days": 365,
    },
    "strawberry": {
        "price_score": 90, "demand": "high", "export": 70,
        "water_need": "Medium", "season": "Rabi",
        "cost_per_acre": 80000, "yield_per_acre": 30, "price_per_quintal": 15000, "cycle_days": 120,
    },
    "pineapple": {
        "price_score": 72, "demand": "medium", "export": 60,
        "water_need": "Medium", "season": "Annual",
        "cost_per_acre": 30000, "yield_per_acre": 60, "price_per_quintal": 3000, "cycle_days": 540,
    },
    "guava": {
        "price_score": 65, "demand": "medium", "export": 45,
        "water_need": "Low", "season": "Annual",
        "cost_per_acre": 20000, "yield_per_acre": 80, "price_per_quintal": 2000, "cycle_days": 365,
    },
    "lemon": {
        "price_score": 70, "demand": "high", "export": 55,
        "water_need": "Low", "season": "Annual",
        "cost_per_acre": 25000, "yield_per_acre": 60, "price_per_quintal": 3500, "cycle_days": 365,
    },
    "mustard": {
        "price_score": 68, "demand": "high", "export": 55,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 12000, "yield_per_acre": 8, "price_per_quintal": 5650, "cycle_days": 110,
    },
    "sunflower": {
        "price_score": 65, "demand": "medium", "export": 45,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 10000, "yield_per_acre": 6, "price_per_quintal": 6760, "cycle_days": 95,
    },
    "soybean": {
        "price_score": 70, "demand": "high", "export": 65,
        "water_need": "Medium", "season": "Kharif",
        "cost_per_acre": 11000, "yield_per_acre": 8, "price_per_quintal": 4600, "cycle_days": 100,
    },
    "groundnut": {
        "price_score": 74, "demand": "high", "export": 60,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 14000, "yield_per_acre": 10, "price_per_quintal": 5850, "cycle_days": 120,
    },
    "sesame": {
        "price_score": 75, "demand": "medium", "export": 70,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 8000, "yield_per_acre": 4, "price_per_quintal": 9000, "cycle_days": 90,
    },
    "castor": {
        "price_score": 68, "demand": "medium", "export": 75,
        "water_need": "Low", "season": "Kharif",
        "cost_per_acre": 9000, "yield_per_acre": 7, "price_per_quintal": 6300, "cycle_days": 180,
    },
    "coriander": {
        "price_score": 72, "demand": "medium", "export": 65,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 10000, "yield_per_acre": 5, "price_per_quintal": 8000, "cycle_days": 90,
    },
    "cumin": {
        "price_score": 80, "demand": "high", "export": 80,
        "water_need": "Low", "season": "Rabi",
        "cost_per_acre": 12000, "yield_per_acre": 4, "price_per_quintal": 18000, "cycle_days": 100,
    },
    "cardamom": {
        "price_score": 95, "demand": "high", "export": 90,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 60000, "yield_per_acre": 2, "price_per_quintal": 250000, "cycle_days": 365,
    },
    "pepper": {
        "price_score": 90, "demand": "high", "export": 88,
        "water_need": "High", "season": "Annual",
        "cost_per_acre": 45000, "yield_per_acre": 4, "price_per_quintal": 50000, "cycle_days": 365,
    },
}

# Demand tier → numeric score
DEMAND_SCORES = {"high": 100, "medium": 65, "low": 35}

# ─── Tag definitions per crop ──────────────────────────────────────────────────
CROP_TAGS: dict[str, list[str]] = {
    "rice":        ["Staple Crop", "High Export", "Kharif Season"],
    "wheat":       ["Staple Crop", "High MSP", "Rabi Season"],
    "maize":       ["Versatile Crop", "Animal Feed", "High Demand"],
    "chickpea":    ["High Protein", "Rabi Season", "Low Water"],
    "kidneybeans": ["Premium Pulse", "High Value", "Kharif Season"],
    "pigeonpeas":  ["Drought Tolerant", "High MSP", "Kharif Season"],
    "mothbeans":   ["Drought Tolerant", "Low Water", "Hardy Crop"],
    "mungbean":    ["Fast Growing", "High Protein", "Low Water"],
    "blackgram":   ["High Protein", "High MSP", "Low Water"],
    "lentil":      ["High Protein", "Low Water", "Rabi Season"],
    "pomegranate": ["Premium Fruit", "High Export", "Low Water"],
    "banana":      ["Year-Round", "High Demand", "Export Crop"],
    "mango":       ["Export Crop", "Premium Price", "High MSP"],
    "grapes":      ["Export Crop", "Premium Price", "Wine Industry"],
    "watermelon":  ["Summer Crop", "High Yield", "Quick Return"],
    "muskmelon":   ["Summer Crop", "Good Margins", "Zaid Season"],
    "apple":       ["Premium Fruit", "Hill Crop", "High MSP"],
    "orange":      ["High Demand", "Export Crop", "Good Margins"],
    "papaya":      ["Year-Round", "Medicinal Value", "Fast Growing"],
    "coconut":     ["Multi-Use", "Export Crop", "Perennial"],
    "cotton":      ["High MSP", "Export Crop", "Kharif Season"],
    "jute":        ["Eco-Friendly", "Export Crop", "Industrial Use"],
    "coffee":      ["Premium Crop", "High Export", "Global Demand"],
    "tomato":      ["High Yield", "Quick Return", "Rabi Season"],
    "potato":      ["Staple Vegetable", "High Yield", "Rabi Season"],
    "onion":       ["Export Crop", "High Demand", "Storage Crop"],
    "garlic":      ["High MSP", "Medicinal Value", "Low Water"],
    "ginger":      ["Spice Crop", "High Export", "Medicinal Value"],
    "turmeric":    ["Spice Crop", "High Export", "Anti-inflammatory"],
    "chilli":      ["Spice Crop", "High Export", "Global Demand"],
    "capsicum":    ["Premium Vegetable", "Export Crop", "Good Margins"],
    "cabbage":     ["Rabi Season", "High Yield", "Leafy Vegetable"],
    "cauliflower": ["Rabi Season", "High Yield", "Brassica Crop"],
    "spinach":     ["Fast Growing", "Short Cycle", "Nutritious"],
    "carrot":      ["Root Vegetable", "Export Potential", "Rabi Season"],
    "radish":      ["Fastest Cycle", "Easy to Grow", "Root Crop"],
    "sweet_potato":["Hardy Crop", "Nutritious", "Drought Tolerant"],
    "sugarcane":   ["Cash Crop", "Industrial Use", "High Yield"],
    "tobacco":     ["Cash Crop", "High Export", "Rabi Season"],
    "tea":         ["Plantation Crop", "High Export", "Premium Brand"],
    "rubber":      ["Industrial Crop", "Perennial", "Export Commodity"],
    "cashew":      ["Drought Tolerant", "Premium Export", "Perennial"],
    "strawberry":  ["Premium Fruit", "High Value", "Cold Weather"],
    "pineapple":   ["Tropical Fruit", "Export Crop", "Vitamin Rich"],
    "guava":       ["Drought Tolerant", "Year-Round", "Nutritious"],
    "lemon":       ["Citrus Crop", "Year-Round", "High Demand"],
    "mustard":     ["Oilseed Crop", "Rabi Season", "Dual Purpose"],
    "sunflower":   ["Oilseed Crop", "Drought Tolerant", "Short Cycle"],
    "soybean":     ["Protein Crop", "Oilseed", "Kharif Season"],
    "groundnut":   ["Oilseed Crop", "Drought Tolerant", "High Protein"],
    "sesame":      ["Premium Oilseed", "High Export", "Low Water"],
    "castor":      ["Industrial Oilseed", "Drought Tolerant", "Export"],
    "coriander":   ["Spice Crop", "Dual Purpose", "Quick Return"],
    "cumin":       ["Premium Spice", "High Export", "Low Water"],
    "cardamom":    ["Luxury Spice", "Highest Value", "Global Demand"],
    "pepper":      ["King of Spices", "Premium Export", "Perennial"],
}

# ─── Government Schemes per crop ──────────────────────────────────────────────
GOVT_SCHEMES: dict[str, list[dict]] = {
    "rice": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support for all farmers"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance at subsidized premium; covers flood, drought, pest losses"},
        {"name": "eNAM", "body": "SFAC / Ministry of Agriculture", "benefit": "Online mandi platform for better price discovery and direct market access"},
        {"name": "RKVY", "body": "Ministry of Agriculture", "benefit": "Grants for irrigation, mechanization, and post-harvest storage"},
    ],
    "wheat": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance covering unseasonal rains and drought"},
        {"name": "MSP Procurement", "body": "FCI / State Agencies", "benefit": "Guaranteed procurement at MSP of INR 2,275/quintal (2024-25)"},
        {"name": "NFSM-Wheat", "body": "Ministry of Agriculture", "benefit": "Subsidized seeds, fertilizers and farm machinery for wheat farmers"},
    ],
    "maize": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance at subsidized premium"},
        {"name": "NFSM", "body": "Ministry of Agriculture", "benefit": "Technology demonstrations, seed distribution and input subsidies"},
    ],
    "cotton": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Insurance includes Pink Bollworm damage coverage"},
        {"name": "TMCIL Scheme", "body": "Textile Ministry", "benefit": "Cotton Technology Mission; subsidized BT cotton seeds and pest management"},
        {"name": "eNAM", "body": "SFAC", "benefit": "Better price discovery for raw cotton in notified mandis"},
    ],
    "sugarcane": [
        {"name": "FRP Policy", "body": "CCEA / Central Govt", "benefit": "Fair and Remunerative Price guarantee; currently INR 340/quintal"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance for natural calamities"},
        {"name": "Sugar Development Fund", "body": "Ministry of Food", "benefit": "Soft loans for cane development and yield improvement"},
    ],
    "soybean": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance at 1.5% premium for Kharif crops"},
        {"name": "NFSM-Oilseeds", "body": "Ministry of Agriculture", "benefit": "Seed minikit distribution, training and input subsidies"},
    ],
    "groundnut": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance covering drought and excess rain"},
        {"name": "NFSM-Oilseeds", "body": "Ministry of Agriculture", "benefit": "Input subsidies and technology support for oilseed farmers"},
        {"name": "eNAM", "body": "SFAC", "benefit": "Online mandi for better groundnut price realization"},
    ],
    "mustard": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance at subsidized Rabi rate"},
        {"name": "NFSM-Oilseeds", "body": "Ministry of Agriculture", "benefit": "Seed minikit distribution, IPM demos, and input subsidies for mustard"},
        {"name": "MSP Procurement", "body": "NAFED / State agencies", "benefit": "Guaranteed procurement at MSP of INR 5,650/quintal (2024-25)"},
    ],
    "onion": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "Price Stabilization Fund", "body": "Ministry of Consumer Affairs", "benefit": "Buffer stock procurement during glut to stabilize farm-gate prices"},
        {"name": "RKVY", "body": "Ministry of Agriculture", "benefit": "Cold storage and pack-house subsidy for onion farmers"},
    ],
    "tomato": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance for horticulture crops (area-based)"},
        {"name": "MIDH", "body": "Ministry of Agriculture", "benefit": "Mission for Integrated Development of Horticulture — subsidized greenhouse, drip irrigation"},
    ],
    "potato": [
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Crop insurance for potato crop losses"},
        {"name": "MIDH", "body": "NHB / Ministry of Agriculture", "benefit": "Cold storage subsidy up to 35% of project cost under NHM"},
    ],
    "mango": [
        {"name": "MIDH", "body": "Ministry of Agriculture", "benefit": "50% subsidy on new horticulture plantation establishment"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "Quality certification, packaging support, and export market development for mangoes"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "PMFBY", "body": "Agriculture Insurance Company", "benefit": "Insurance against cyclone and unseasonal rain losses"},
    ],
    "banana": [
        {"name": "MIDH", "body": "Ministry of Agriculture", "benefit": "Subsidy for tissue culture planting material (up to 50%)"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "Export market facilitation and quality packaging support"},
    ],
    "grapes": [
        {"name": "MIDH", "body": "Ministry of Agriculture", "benefit": "50% subsidy on establishment of new vineyard, drip irrigation"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "EurepGAP certification support; export market development"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
    ],
    "coffee": [
        {"name": "Coffee Board Subsidies", "body": "Coffee Board of India", "benefit": "Replanting subsidy, organic certification support, export promotion"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "GI Tag Protection", "body": "Coffee Board", "benefit": "Coorg, Araku, and Chikmagalur coffees have GI protection for premium market access"},
    ],
    "tea": [
        {"name": "Tea Board Subsidies", "body": "Tea Board of India", "benefit": "Replanting, rejuvenation subsidy; quality upgradation grants"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
        {"name": "Quality Upgradation Scheme", "body": "Tea Board", "benefit": "Subsidy for manufacturing equipment and food safety certification"},
    ],
    "cardamom": [
        {"name": "Spices Board Subsidies", "body": "Spices Board of India", "benefit": "Subsidy for replanting, post-harvest, organic certification"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "Export market development, international quality standards support"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
    ],
    "pepper": [
        {"name": "Spices Board Subsidies", "body": "Spices Board of India", "benefit": "Replanting subsidy, post-harvest development, and organic certification support"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "Export promotion, quality testing labs, and trade facilitation"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
    ],
    "turmeric": [
        {"name": "Spices Board Subsidies", "body": "Spices Board of India", "benefit": "Post-harvest handling, organic certification, and quality testing support"},
        {"name": "APEDA Export Promotion", "body": "APEDA", "benefit": "Export market development and trade facilitation"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
    ],
    "ginger": [
        {"name": "Spices Board Subsidies", "body": "Spices Board of India", "benefit": "Seed rhizome subsidy, post-harvest development grants"},
        {"name": "MIDH", "body": "Ministry of Agriculture", "benefit": "Assistance for spice development under NHM/MIDH"},
        {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support"},
    ],
}

# Default schemes for any crop not specifically listed
DEFAULT_SCHEMES = [
    {"name": "PM-KISAN", "body": "Ministry of Agriculture", "benefit": "INR 6,000/year direct income support transferred to all farmer families"},
    {"name": "PMFBY", "body": "Agriculture Insurance Company of India", "benefit": "Pradhan Mantri Fasal Bima Yojana — subsidized crop insurance for natural calamity losses"},
    {"name": "eNAM", "body": "SFAC / Ministry of Agriculture", "benefit": "National Agriculture Market — online trading platform for better price realization"},
    {"name": "RKVY", "body": "Ministry of Agriculture", "benefit": "Rashtriya Krishi Vikas Yojana — state-level agricultural development grants"},
]

# ─── AI Insights per crop ─────────────────────────────────────────────────────
AI_INSIGHTS: dict[str, str] = {
    "rice": "Rice is India's primary Kharif staple, thriving in standing-water paddy systems. Transplanting 25-day-old seedlings at 20×15 cm spacing maximizes tillering. Use SRI (System of Rice Intensification) to cut water use 30% while boosting yields 20-40%. Key pests include Brown Plant Hopper and Stem Borer — use pheromone traps and neem-based sprays as IPM first line. Blast disease (Magnaporthe oryzae) is managed with Tricyclazole at pre-heading stage. Intercrop with azolla to bio-fix nitrogen, reducing urea requirement by 25 kg/acre. Consider direct seeded rice (DSR) for labor savings of INR 3,000–5,000/acre. Harvest at 80% grain maturity (golden yellow) to prevent shattering losses.",
    "wheat": "Wheat performs best on well-drained loamy soils of the Indo-Gangetic Plain. Sow in the first fortnight of November for optimum yields — late sowing reduces yield 30-40 kg/ha per day. Use certified HI-8498, HD-2967, or DBW-187 varieties for higher MSP eligibility. Yellow rust (Puccinia striiformis) is the primary disease threat — grow resistant varieties like PBW-343. Crown wheat with 3-4 irrigations at Crown Root Initiation (CRI), Tillering, Jointing, and Grain-filling stages. Terminal heat stress above 35°C at grain fill reduces yield significantly — timely sowing is the best mitigation. Mechanized harvesting with combines cuts post-harvest losses from 10% to 2%.",
    "maize": "Maize is one of India's most versatile crops with food, feed, starch, and fuel applications. Use hybrid seeds (NK-6240, DKC-9144) for yield 40-60% higher than open-pollinated varieties. Plant at 65×20 cm spacing, 4-6 cm deep for optimum stand. Maize is highly susceptible to waterlogging — raised bed planting in flood-prone areas is recommended. Fall Armyworm (Spodoptera frugiperda) has emerged as the biggest threat since 2020 — use emamectin benzoate sprays at first sign. Intercrop with soybean in 2:1 or 4:2 row ratios for 30% higher system productivity. For high-value market, cultivate baby corn (harvest at silking, 45 days) or sweet corn for 3-4x revenue premium. Drip fertigation reduces water use 40% and improves nitrogen uptake efficiency.",
    "chickpea": "Chickpea (chana) is India's most important pulse crop, contributing 40% of total pulse production. Desi varieties (JG-11, JG-14) are preferred for drought tolerance; Kabuli types fetch 2x premium in export markets. Sow at optimal depth (8-10 cm) in well-drained soils after the last rice harvest. Rhizobium inoculation of seeds reduces nitrogen requirement completely — a major cost saving. Collar rot (Sclerotium rolfsii) and Fusarium wilt are key disease risks — use Trichoderma seed treatment and resistant varieties. Avoid overirrigation — chickpea is highly drought-tolerant and excess moisture promotes wilt diseases. Market as whole grain for staple use or as kabuli for export premium through NAFED or private traders.",
    "cotton": "Cotton is India's most important cash crop and primary fiber for the textile industry. BT cotton varieties dominate — select based on bollworm resistance and regional adaptation. Sow at 90×60 cm spacing in Kharif on deep black soils (vertisols). Pink Bollworm (PBW) has developed resistance to Bt toxins in Gujarat — use refuge planting (20% non-Bt rows) and pheromone traps. Adopt Integrated Pest Management: release Chrysoperla larvae for early aphid and whitefly control. Key deficiencies: Sulfur and Boron — supplement during boll development for better retting quality. Water stress at squaring and flowering stages reduces yields 40-60% — ensure irrigation if monsoon is deficient. Harvest manually for seed-cotton purity; quality ginning factors: staple length, micronaire, strength — use ASTM standards.",
    "sugarcane": "Sugarcane is the world's largest cultivated crop by volume, and India is the second-largest producer. Ratoon cropping (from stubble) saves 30-40% replanting cost; maintain 2-3 ratoon cycles before replanting. Plant trench sets (2-eye sets) at 90-cm row spacing; apply Trichoderma + PSB + Azospirillum seed treatment. Water is the critical input — sugarcane needs 1,500-2,500 mm total water; drip irrigation boosts yield 30% and saves 40% water. Borers (top shoot borer, stem borer, root borer) are key pests — release Trichogramma cards at 1.5 lakh/ha at 30-day intervals. Harvest at peak sucrose maturity (Brix 18-20°); crushing delay beyond 24 hours drops sucrose 0.2% per hour. Coordinate with mill for timely harvesting schedule to avoid sucrose inversion losses.",
    "soybean": "Soybean is called the 'Golden Bean' of Indian agriculture for its dual oil-protein value. Use certified varieties: JS-335, JS-9560, MAUS-71 for central India; NRC-37 for East India. Sow promptly at monsoon onset in June — delayed sowing (after July 15) reduces yields 40-50 kg/acre per week. Rhizobium (Bradyrhizobium japonicum) seed inoculation eliminates nitrogen requirement; combined with PSB provides full phosphorus nutrition. Girdle Beetle has re-emerged as a critical pest in MP and Maharashtra — apply thiamethoxam 25% WG at ETL. Harvest at 92-95% pod maturity (yellow pods with brown seeds) to prevent shattering — early morning combine harvesting minimizes losses. Process into oil (18-20% oil content) or soy meal (protein 40-45%); meal fetches premium from poultry industry in Maharashtra.",
    "groundnut": "Groundnut (peanut) is India's primary oilseed crop with dual food and industrial use. Use improved varieties: GG-20, GJG-9 for Gujarat; K-6, TMV-7 for Tamil Nadu; ICGV-86590 for Rajasthan. Pre-sow irrigation (palewa) ensures even germination in semi-arid soils. Gypsum application (200 kg/acre) at pegging stage is essential for pod development — boron deficiency causes internal kernel disorders. Early and Late Leaf Spot diseases are managed with Mancozeb spray at 10-day intervals. Harvest before rains to avoid aflatoxin contamination (Aspergillus flavus) — aflatoxin makes groundnuts unmarketable for export. Bold-kernel varieties (SB-11, ICGV-00350) fetch 20-30% price premium in confectionery market. Process into peanut butter, roasted snacks, or cold-press oil for 4-5x value addition.",
    "tomato": "Tomato is India's most economically important horticultural vegetable with very high income potential per acre. Transplant 25-35 day old seedlings in raised beds at 60×45 cm spacing using drip irrigation for best results. Use hybrid varieties for disease resistance and high yield: Arka Rakshak (bacterial wilt resistant), Pusa Hybrid-1, or Naveen F1. The crop has 3-4 price cycles annually — timing planting to peak festival demand (Navratri, Diwali) can multiply revenues 3-5x. Early Blight (Alternaria solani) and Late Blight (Phytophthora infestans) are primary disease threats — use protectant fungicides preventively. Fruitworm (Helicoverpa armigera) is the key pest — use pheromone traps and NPV spray at 1 lakh PoB/ha. Value addition as tomato puree, ketchup, or dried tomatoes prevents distress sale during market glut. Consider polyhouse cultivation for off-season premium pricing.",
    "potato": "Potato is the world's fourth-largest food crop and provides highest caloric yield per unit land area. Use certified disease-free seed tubers — Kufri Jyoti, Kufri Bahar, Kufri Chipsona (for processing). Plant 5-6 cm seeds at 20×60 cm spacing in ridges for easy earthing-up. Late Blight (Phytophthora infestans) is the single biggest risk — apply Mancozeb or Metalaxyl preventively every 7-10 days during cool, humid spells. Cold storage (2-4°C, 90% RH) extends marketing period from 2 months to 9 months — critical for price management. Process into chips, fries, or flakes for 5-8x value addition; Chipsona varieties have preferred chip color (low reducing sugars). Seed potato production (for next season planting) fetches 3x higher price than table potato. The UP-Punjab belt dominates production; Shekhawati (Rajasthan) emerging as significant winter potato zone.",
    "onion": "Onion is a strategic vegetable that drives political attention due to price volatility — presenting both risk and opportunity. Use NHRDF-Red, Agrifound-Dark-Red, or Bhima-Raj varieties suited to your region; NHRDF varieties have better storage life. Transplant 6-7 week old nursery seedlings at 10×7.5 cm spacing on ridges under raised bed planting. Purple Blotch (Alternaria porri) and Thrips are primary pest-disease problems — spray Imidacloprid for thrips management. Bulb initiation requires 12-14 hours of daylight — so variety selection based on photoperiod response and latitude is critical. Cure harvested onions under shade for 2-3 weeks to develop papery skins for storage — reduces storage losses from 30% to under 10%. NAFED buffer stock operations stabilize prices — enroll through state marketing federation for assured procurement.",
    "ginger": "Ginger is one of India's most profitable spice crops — high value per acre justifies intensive management. Use certified disease-free rhizomes (India's biggest production risk is Soft Rot/Pythium); Maran and Nadia varieties are popular in NE India; Himachal and Rio-de-Janeiro in Kerala. Plant 2-2.5 cm rhizomes in 30×25 cm spacing under 50% shade nets for best yield. Soil-borne diseases (Pythium Soft Rot) are the critical risk — raised bed planting with excellent drainage, Trichoderma soil application, and bordeaux mixture prophylactic sprays are essential. Ginger requires 3 earthing-up operations during the growing season; each earthing increases yield 15-20%. Harvest for dry ginger at 8-9 months (fiber content high); for fresh market at 5-6 months. Up-country markets fetch best prices for fresh ginger (Mumbai, Delhi, Kolkata). Dried ginger and ginger powder have strong export demand — UAE, USA, UK are primary buyers.",
    "turmeric": "Turmeric is the 'Golden Spice' with its health benefits driving sustained global demand growth. Choose varieties based on curcumin: Lakadong (Meghalaya) has 9% curcumin vs. commercial 2.5-3.5% — commands 10x premium in nutraceutical market. Plant at 30×20 cm spacing in well-drained, loamy soils with excellent organic matter. Rhizome rot (Pythium) is the most serious disease — soil drenching with Metalaxyl at 45 and 90 days after planting is preventive. Thrips damage decreases curcumin content — use reflective mulch and imidacloprid for IPM management. Boiling and drying is critical for quality: sun-dry slowly for 2-3 weeks; use polishing for uniform color. Organic turmeric (NPOP certified) fetches 40-60% premium in both domestic and export markets. GI-tagged varieties (Sangli turmeric, Erode turmeric) fetch even higher premiums — pursue state GI certification.",
    "chilli": "Chilli is India's largest spice export earner — Guntur cluster alone contributes 30% of world chilli trade. Use hybrid varieties for high yield with disease resistance: Arnav-5, Arka Meghana, LCA-206 for Andhra Pradesh. Transplant 4-5 week old seedlings at 60×45 cm spacing; install drip irrigation for 40% water saving. Anthracnose (Colletotrichum capsici) and Viral diseases (TYLCV, CMV) are primary threats — use virus-free seedlings and yellow sticky traps for whitefly vectors. Chilli drying on open roads causes mycotoxin contamination — use tarpaulin or mechanical dryers for export-quality product. Oleoresin extraction (for food, pharma, defense industries) provides premium value addition opportunity. Guntur, Byadagi (smooth, red color) and Bird's Eye (hotness, Thai cuisine) varieties command international premium prices.",
    "mustard": "Mustard is India's most important Rabi oilseed — critical for domestic edible oil security. Use improved varieties: DRMR-150-35, NRCHB-506, Pusa Bold; new double-zero (canola-type) varieties for premium market. Sow timely (October 10-25 in north India) at 7.5-10 cm row spacing for optimum plant population. Aphid is the critical pest — single spray of Dimethoate or Imidacloprid when colony infestation reaches 37 aphids/plant; early intervention is critical because infestation doubles every 2-3 days. White Rust (Albugo candida) causes significant seed yield loss — grow resistant varieties or apply Metalaxyl-M + Mancozeb. Harvest when 75% of pods turn straw-colored for minimum shattering losses; delay causes 30-40% shattering. Double-zero (low erucic acid, low glucosinolate) varieties have premium demand for human consumption and export market.",
    "sunflower": "Sunflower offers reliable income with drought tolerance and short crop cycle (90-95 days). Hybrid varieties (KBSH-44, PAC-306, Surya, DRSF-108) give 30-50% yield advantage over open-pollinated types. Sow in kharif (June-July) or rabi (October-November) — versatile across seasons. Bird damage during grain filling is a serious concern in most locations — use bird-scaring devices or netting for 10-15% yield protection. Stem boring caterpillar and Spodoptera — use Chlorpyrifos and pheromone traps. Sunflower oil has premium nutraceutical positioning (high oleic acid) — Altasol varieties fetch 20% over standard sunflower. Alternate rows of pollinator strips attract bees which improve seed set 30-40% — essential for hybrid seed production. Sunflower head stover is excellent cattle feed and biodegradable mulch material.",
    "cumin": "Cumin (jeera) is India's most exported spice — Rajasthan-Gujarat belt is the world's largest producer. Use improved varieties: GC-4, RZ-19, RZ-209 for better yield and essential oil content. Ideal sowing window (October 25 - November 10) is narrow — late sowing causes 40% yield reduction due to powdery mildew susceptibility in warm weather. Alternaria Leaf Spot, Wilt, and Powdery Mildew are the devastating disease triad — use crop rotation with mustard, avoid rice-heavy soils, and apply Hexaconazole at first symptoms. Cumin needs cool, dry weather at 15-25°C — Gujarat coastal districts and Rajasthan perform best. Harvest at 60% crop maturity for essential oil retention — early morning threshing minimizes oil volatilization. Premium market: organic certified cumin exports to EU/USA fetch INR 25,000-40,000/quintal — triple the conventional price. Store in airtight containers to preserve essential oil content (cuminaldehyde).",
    "cardamom": "Cardamom is the world's third most expensive spice — 'Queen of Spices' with extraordinary value per acre. Clone-based propagation (Mudigere-1, CCS-1, Njallani) ensures early and uniform bearing. Shade management (40-50% shade) under silver oak or banana canopy is non-negotiable for quality. Thrips (Frankliniella oceanica) devastate capsule set — yellow sticky traps at 4/acre and Spinosad spray management is essential. Katte disease (Mosaic Virus) has no cure — rogue and destroy infected plants immediately; use certified disease-free planting material only. Post-harvest curing is critical for quality — use cardamom curer (low-temperature dryer) to achieve bright green color; traditional Rum-cure gives inferior golden color. Export directly to spice traders in Idukki, Coimbatore, or through Cardamom Hill Reserve auctions for price discovery. Organic cardamom (NPOP certified) fetches 50-80% premium in European and US gourmet markets.",
    "pepper": "Black pepper is the 'King of Spices' and India's most historically significant export crop. Use Panniyur-1, Sreekara, Subhakara varieties — suited to Kerala's humid conditions. Train on living standards (arecanut, coconut, silver oak) at 3×3 m spacing for maximum sunshine utilization. Phytophthora Foot Rot is the single most serious disease — Bordeaux Mixture prophylactic soil drench (3 times: March, June, September) is mandatory. Spike shedding and slow decline are nutrient-deficiency related — balanced NPK+Mg+Zn fertilization through foliar spray during monsoon. Harvest spikes when 5-10% berries turn red for best pungency (piperine content highest at this stage). Primary processing: compost husk for organic certification; wash and dry on raised platforms for food safety. White pepper (decorticulated) fetches premium in EU markets; use HACCP-certified processing for export.",
    "tea": "Tea plantation is a long-term investment with returns from year 4 onwards — sustainable management is key. Clone-based planting (TV-25, UPASI-9, K-1) gives 40% higher yields than seedling tea. Pruning cycle (hard prune every 4-5 years, medium prune intermediate years) directly controls leaf area index and quality. Helopeltis (Tea Mosquito Bug) and Red Spider Mite are primary pests — integrated pest management using biocontrol (Amblyseius cucumeris mite) reduces pesticide cost. For premium orthodox tea: two-leaves-and-bud harvesting standard (tipping) maintained at 7-10 day intervals; 10-day flush cycle in peak season produces fine Darjeeling-style flush teas. Darjeeling First Flush (March-April) commands INR 10,000-50,000/kg globally; direct estate marketing through auctions or D2C online channels. Orthodox (whole leaf) > CTC (crush-tear-curl) > green tea — value addition hierarchy; green and white teas are fastest growing segments globally.",
    "coffee": "Coffee cultivation is one of India's most successful agro-forestry systems — Indian robusta and arabica both fetch premiums for shade-grown, sustainable production. Arabica: suited to 1,000-1,500m altitude (Chikmagalur, Coorg, Nilgiris); high quality, delicate flavor; Robusta: 500-1,000m (Wayanad, Coorg lowlands); heavier body, higher caffeine. Berry Borer (Hypothenemus hampei) is the most important pest — apply Beauveria bassiana biocontrol at berry color change stage. White Stem Borer attacks all ages of plantation — use neem cake soil application and trunk injection of imidacloprid. Harvest selectively (hand-picking red cherries only) for specialty-grade coffee; strip harvesting for higher volume but lower quality. Pulped Natural (honey processed), Washed Arabica, and Wine processed coffees fetch INR 500-2,000/kg green vs. INR 200-350/kg for standard parchment. Indian specialty coffee (Monsooned Malabar, Coorg Estate) is recognized globally in specialty coffee circles.",
}

DEFAULT_INSIGHT = (
    "This crop presents strong agronomic suitability for your soil profile. "
    "Key management practices: adopt Integrated Pest Management (IPM) to reduce chemical inputs; "
    "apply balanced NPK fertilization based on soil test results; use certified improved varieties "
    "for yield advantage over open-pollinated types; implement water-saving drip irrigation for "
    "25-40% reduction in water requirements while boosting productivity. "
    "Government support is available through PM-KISAN (direct income support), PMFBY (crop insurance), "
    "and eNAM (online market platform). Explore value addition through FPO membership for better "
    "collective bargaining at mandis. Keep records of input costs and yields for bank loan eligibility "
    "under KCC (Kisan Credit Card) at 7% interest rate."
)


def get_market_score(crop_name: str) -> dict:
    """
    Return the composite market score dict for a given crop name.
    Composite market_score = 0.40 * price_score + 0.40 * demand_score + 0.20 * export
    """
    crop_lower = crop_name.lower()
    data = MARKET_SCORES.get(crop_lower)
    if data is None:
        return {
            "market_score": 50,
            "demand": "medium",
            "water_need": "Medium",
            "season": "Kharif",
            "tags": [],
            "govt_schemes": DEFAULT_SCHEMES,
            "ai_insights": DEFAULT_INSIGHT,
            "cost_per_acre": 15000,
            "yield_per_acre": 10,
            "price_per_quintal": 3000,
            "cycle_days": 120,
        }

    demand_score = DEMAND_SCORES[data["demand"]]
    composite = round(
        0.40 * data["price_score"] + 0.40 * demand_score + 0.20 * data["export"]
    )
    tags = CROP_TAGS.get(crop_lower, [])
    schemes = GOVT_SCHEMES.get(crop_lower, DEFAULT_SCHEMES)
    insight = AI_INSIGHTS.get(crop_lower, DEFAULT_INSIGHT)

    return {
        "market_score": composite,
        "demand": data["demand"],
        "water_need": data["water_need"],
        "season": data["season"],
        "tags": tags,
        "govt_schemes": schemes,
        "ai_insights": insight,
        "cost_per_acre": data["cost_per_acre"],
        "yield_per_acre": data["yield_per_acre"],
        "price_per_quintal": data["price_per_quintal"],
        "cycle_days": data["cycle_days"],
    }
