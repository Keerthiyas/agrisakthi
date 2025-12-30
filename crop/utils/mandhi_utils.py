def infer_soil_from_weed(weed):
    weed_map = {
        "Crabgrass": {
            "soil": "Sandy",
            "moisture": "Low",
            "nutrients": "Low",
            "weed_pressure": "High"
        },
        "Nutgrass": {
            "soil": "Clay",
            "moisture": "High",
            "nutrients": "Medium",
            "weed_pressure": "Medium"
        }
    }

    return weed_map.get(weed, {
        "soil": "Unknown",
        "moisture": "Medium",
        "nutrients": "Medium",
        "weed_pressure": "Low"
    })
CROPS = [
    {
        "name": "Pearl Millet",
        "soil": ["Sandy"],
        "water": "Low",
        "weed_tolerance": "High"
    },
    {
        "name": "Groundnut",
        "soil": ["Sandy", "Loamy"],
        "water": "Medium",
        "weed_tolerance": "Medium"
    },
    {
        "name": "Paddy",
        "soil": ["Clay"],
        "water": "High",
        "weed_tolerance": "Low"
    }
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
