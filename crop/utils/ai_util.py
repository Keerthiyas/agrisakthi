import random

def get_crop_suggestion_from_image(image_url):
    """
    Simulate weed detection, soil pH, and moisture.
    Suggest crops based on all parameters.
    """
    # Simulate weed detection
    detection = random.choice(["Weed Detected", "No Weed Detected"])
    
    # Simulate soil pH
    soil_ph = round(random.uniform(4.0, 8.0), 1)
    
    # Simulate moisture
    moisture = random.choice(["Low", "Medium", "High"])
    
    # Simple recommendation logic
    crops = []
    
    if detection == "Weed Detected":
        crops.extend(["Corn", "Wheat"])  # weed-tolerant
    else:
        crops.extend(["Tomato", "Rice"])  # high-value
    
    # Adjust based on pH
    if soil_ph < 5.5:
        crops.append("Potato")  # acid-tolerant
    elif soil_ph > 7.5:
        crops.append("Barley")  # alkaline-tolerant
    
    # Adjust based on moisture
    if moisture == "Low":
        crops.append("Millet")  # drought-tolerant
    
    recommendation = ", ".join(crops)
    
    # Return all simulated info
    info = {
        "detection": detection,
        "soil_ph": soil_ph,
        "moisture": moisture,
        "recommendation": recommendation
    }
    
    return info
