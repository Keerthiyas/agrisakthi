def generate_explanation(weed, soil, weather, recommended, avoided):
    return f"""
Detected weed: {weed}, which indicates {soil['soil']} soil with {soil['moisture']} moisture.
Current weather shows temperature around {weather['temperature']}°C.

Recommended crops are chosen because they tolerate weed competition and match soil conditions.
Crops listed under avoid have higher risk due to water stress or weed pressure.

This recommendation focuses on reducing cultivation risk rather than only maximizing yield.

"""
