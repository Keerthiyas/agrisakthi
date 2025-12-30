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

def infer_soil_from_weed(weed):
    weed_map = {
        "Crabgrass": {"soil": "Sandy", "moisture": "Low", "nutrients": "Low", "weed_pressure": "High"},
        "Nutgrass": {"soil": "Clay", "moisture": "High", "nutrients": "Medium", "weed_pressure": "Medium"}
    }
    return weed_map.get(weed, {"soil": "Unknown", "moisture": "Medium", "nutrients": "Medium", "weed_pressure": "Low"})

CROPS = [
    {"name": "Pearl Millet", "soil": ["Sandy"], "water": "Low", "weed_tolerance": "High"},
    {"name": "Groundnut", "soil": ["Sandy", "Loamy"], "water": "Medium", "weed_tolerance": "Medium"},
    {"name": "Paddy", "soil": ["Clay"], "water": "High", "weed_tolerance": "Low"},
    {"name": "Sorghum", "soil": ["Clay", "Loamy"], "water": "Medium", "weed_tolerance": "High"},
    {"name": "Millet", "soil": ["Clay", "Sandy"], "water": "Low", "weed_tolerance": "Medium"},
    {"name": "Wheat", "soil": ["Clay", "Loamy"], "water": "Medium", "weed_tolerance": "Medium"},
    {"name": "Rice", "soil": ["Clay"], "water": "High", "weed_tolerance": "Low"},
    {"name": "Tomato", "soil": ["Sandy", "Loamy"], "water": "Medium", "weed_tolerance": "Medium"},
    {"name": "Groundnut", "soil": ["Sandy", "Loamy"], "water": "Medium", "weed_tolerance": "Medium"},
]

def recommend_crops(soil_info, weather):
    recommended = []
    avoided = []
    for crop in CROPS:
        risk = []
        if soil_info["soil"] not in crop["soil"]:
            risk.append("Unsuitable soil")
        if soil_info["weed_pressure"] == "High" and crop["weed_tolerance"] == "Low":
            risk.append("High weed competition")
        if soil_info["moisture"] == "Low" and crop["water"] == "High":
            risk.append("Water stress risk")
        if risk:
            avoided.append({"crop": crop["name"], "reason": ", ".join(risk)})
        else:
            recommended.append(crop["name"])
    return recommended[:5], avoided
