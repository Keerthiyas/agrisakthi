# crop/utils/mandi_utils.py
from math import radians, cos, sin, asin, sqrt

TRANSPORT_COST = {
    "road": 20,
    "rail": 15,
    "air": 50
}

MANDIS_DB = [
    {"market_name": "Palladam Mandi", "lat": 11.010, "lon": 76.650, "price_per_kg": 200},
    {"market_name": "Udumalpet Mandi", "lat": 10.980, "lon": 76.550, "price_per_kg": 195},
    {"market_name": "Madathukulam Mandi", "lat": 10.900, "lon": 76.600, "price_per_kg": 198},
]

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6371 * c
    return km

def get_nearby_mandi(crop_name, lat, lon, transport="road", quantity_kg=100, charge_per_km=None, top_n=3):
    charge_per_km = charge_per_km if charge_per_km is not None else TRANSPORT_COST.get(transport, 20)
    
    mandis = []
    for m in MANDIS_DB:
        distance = haversine(lat, lon, m["lat"], m["lon"])
        transport_cost_per_kg = (distance * charge_per_km) / 1000  
        profit_per_kg = m["price_per_kg"] - transport_cost_per_kg
        mandis.append({
            "market_name": m["market_name"],
            "crop_name": crop_name,
            "price_per_kg": m["price_per_kg"],
            "distance_km": round(distance, 2),
            "transport_cost_per_kg": round(transport_cost_per_kg, 2),
            "profit_per_kg": round(profit_per_kg, 2)
        })
    
    mandis = sorted(mandis, key=lambda x: x["profit_per_kg"], reverse=True)
    return mandis[:top_n]
# crop/utils/mandi_utils.py
import json
import re
import google.generativeai as genai

def recommend_crops(soil_info, weather):

    prompt = f"""
You are an expert agronomist AI for Indian agriculture.

Field Conditions:

Soil:
- Soil type: {soil_info.get('soil')}
- Moisture: {soil_info.get('moisture')}
- Nutrient level: {soil_info.get('nutrients')}
- pH: {soil_info.get('pH')}

Weather:
- Temperature: {weather.get('temperature')} °C
- Rainfall: {weather.get('rainfall')} mm
- Humidity: {weather.get('humidity')} %
- Wind: {weather.get('wind')} m/s

Task:
Recommend crops using scientific reasoning based on:
1. Soil type suitability
2. Nitrogen / nutrient level
3. Rainfall requirement of crop
4. Temperature range suitability
5. Moisture compatibility

Scientific Rules:

- If nutrients are LOW → prefer nitrogen-efficient crops OR mention fertilizer improvement in reason.
- If rainfall > 150 mm → prefer water-tolerant crops (e.g., paddy).
- If rainfall < 50 mm → prefer drought-resistant crops (millets, pulses).
- If temperature > 32°C → prefer heat-tolerant crops.
- If temperature < 20°C → prefer cool-season crops.
- Match soil type with suitable crops.
- Avoid crops that mismatch rainfall, temperature, or nutrient condition.

STRICT RULES:
- Recommend 3 to 5 Indian crops (never zero).
- Suggest 3 to 5 crops to avoid.
- Each recommended crop must have:
   - name
   - score (0–100)
- Avoid explanation outside JSON.
- Return ONLY valid JSON.

JSON FORMAT:
{{
  "recommended": [
    {{
      "name": "Crop name",
      "score": 85
    }}
  ],
  "avoided": [
    {{
      "crop": "Crop name",
      "reason": "Short reason based on rainfall, temperature or nutrient mismatch"
    }}
  ]
}}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    raw_text = response.text.strip()

    # 🔥 REMOVE MARKDOWN BLOCKS IF PRESENT
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        data = json.loads(raw_text)
        return data["recommended"], data["avoided"]

    except Exception as e:
        print("❌ Gemini JSON parse error:", e)
        print("❌ Gemini raw output:", raw_text)

        # Safe fallback (never empty → UI won’t break)
        return [
            {"name": "Millet", "score": 70},
            {"name": "Sorghum", "score": 68},
            {"name": "Maize", "score": 65},
        ], [
            {"crop": "Sugarcane", "reason": "High water requirement"},
            {"crop": "Rice", "reason": "Weed sensitivity"},
        ]
import json
import re
import google.generativeai as genai

def infer_soil_from_weed(weed):
    prompt = f"""
You are an expert agronomist AI. A weed named "{weed}" is detected in a farm field.

Based on its presence, infer the field's soil conditions using science-based reasoning.  
Return ONLY JSON with **concise, one-word or very short predictions** suitable for UI boxes:

JSON FORMAT:
{{
  "soil": "Soil type, e.g., Loam, Sandy, Clay, Degraded",
  "moisture": "Good, Moderate, Poor",
  "nutrients": "High, Medium, Low",
  "pH": "Acidic, Neutral, Alkaline"
}}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    raw_text = response.text.strip()
    # Remove markdown code blocks if present
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        # Convert AI output to Python dictionary
        data = json.loads(raw_text)
        # Optional: Ensure all keys exist
        return {
            "soil": data.get("soil", "Unknown"),
            "moisture": data.get("moisture", "Moderate"),
            "nutrients": data.get("nutrients", "Medium"),
            "pH": data.get("pH", "Neutral")
        }
    except Exception as e:
        print("❌ Soil inference error:", e)
        print("❌ Raw output:", raw_text)
        # Safe fallback
        return {
            "soil": "Unknown",
            "moisture": "Moderate",
            "nutrients": "Medium",
            "pH": "Neutral"
        }
