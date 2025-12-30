def recommend_crop_logic(weather, soil_type=None, season=None):
    temp = weather.get("temp")
    humidity = weather.get("humidity")
    rain = weather.get("rain", 0)

    crops = []

    if 20 <= temp <= 30 and rain > 50:
        crops.append("Rice")
    if 18 <= temp <= 28 and humidity < 60:
        crops.append("Wheat")
    if temp > 25 and rain < 40:
        crops.append("Millets")
    if temp > 30 and humidity < 50:
        crops.append("Cotton")

    if season == "Summer":
        crops.append("Maize")
    if season == "Winter":
        crops.append("Mustard")

    return list(set(crops)) or ["Groundnut"]
