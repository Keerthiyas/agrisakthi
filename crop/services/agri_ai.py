def agri_decision_engine(disease, confidence, weather):
    temp = weather["temp"]
    humidity = weather["humidity"]
    rain = weather.get("rain", 0)

    # Disease severity
    if confidence > 80:
        severity = "High"
    elif confidence > 50:
        severity = "Medium"
    else:
        severity = "Low"

    # Soil inference
    if rain > 20:
        soil = "High Moisture Soil"
    elif temp > 32:
        soil = "Dry Soil"
    else:
        soil = "Moderate Soil"

    # Weed risk
    weed_risk = "High" if humidity > 65 and rain > 10 else "Low"

    # Crop decision logic
    if severity == "High":
        crop_action = "Avoid planting new crops. Treat disease first."
    elif soil == "High Moisture Soil":
        crop_action = "Suitable for Paddy or Sugarcane."
    elif soil == "Dry Soil":
        crop_action = "Suitable for Millets or Pulses."
    else:
        crop_action = "Suitable for Groundnut or Maize."

    return {
        "severity": severity,
        "soil": soil,
        "weed_risk": weed_risk,
        "crop_action": crop_action
    }
