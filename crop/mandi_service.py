# crop/mandi_service.py

def get_best_mandi(crop, quantity, transport):
    """
    Hardcoded simple logic to return nearby mandi info.
    """
    # Hardcoded prices
    price_mapping = {"Paddy": 2500, "Wheat": 2000, "Maize": 1800}

    # Hardcoded mandi info
    mandi_info = {
        "Coimbatore": {"distance_km": 15, "location": "Kalapatti"},
    }

    price = price_mapping.get(crop, 0)
    mandi = "Coimbatore"
    distance = mandi_info["Coimbatore"]["distance_km"]

    # Simplified profit calculation: price * quantity - transport cost
    transport_cost = 0
    if transport == "Truck":
        transport_cost = distance * 10
    elif transport == "Bike":
        transport_cost = distance * 5
    elif transport == "Cart":
        transport_cost = distance * 2

    profit = (price * quantity) - transport_cost

    return {
        "mandi": mandi,
        "location": mandi_info[mandi]["location"],
        "distance": distance,
        "price": price,
        "profit": profit,
        "crop": crop,
        "quantity": quantity,
        "transport": transport
    }
