"""
Mandi Analysis Service
Finds nearby high-profit mandis with transport costs for a given location.
"""

import os
import json
import math
import pandas as pd
from datetime import datetime

# Reference mandis near Coimbatore (Tamil Nadu)
REFERENCE_MANDIS = {
    'Coimbatore': {'lat': 11.0083, 'lon': 76.6551, 'state': 'Tamil Nadu'},
    'Palladam': {'lat': 10.9945, 'lon': 77.4075, 'state': 'Tamil Nadu'},
    'Pollachi': {'lat': 10.6568, 'lon': 77.0059, 'state': 'Tamil Nadu'},
    'Udumalpet': {'lat': 10.3305, 'lon': 77.2710, 'state': 'Tamil Nadu'},
    'Madathukulam': {'lat': 10.8684, 'lon': 77.1905, 'state': 'Tamil Nadu'},
}

# Approximate transport costs per km per unit (kg) - typical rates
TRANSPORT_COST_PER_KM_PER_KG = 0.05  # Rs per km per kg (rough estimate)
MIN_SHIPMENT_SIZE = 100  # kg


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km."""
    R = 6371  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def calculate_profit_margin(selling_price, cost_price, transport_cost_per_unit):
    """Calculate profit margin after transport costs."""
    net_price = selling_price - transport_cost_per_unit
    if cost_price <= 0:
        return 0
    margin = ((net_price - cost_price) / cost_price) * 100
    return max(margin, 0)  # Don't show negative as high profit


def find_nearby_mandis(origin_lat, origin_lon, max_distance_km=100):
    """Find mandis within max_distance_km from origin point."""
    nearby = []
    for mandi_name, mandi_data in REFERENCE_MANDIS.items():
        distance = haversine_distance(
            origin_lat, origin_lon,
            mandi_data['lat'], mandi_data['lon']
        )
        if distance <= max_distance_km:
            nearby.append({
                'name': mandi_name,
                'distance_km': round(distance, 2),
                **mandi_data
            })
    
    return sorted(nearby, key=lambda x: x['distance_km'])


def analyze_crop_profit(crop_name, buy_price, nearby_mandis):
    """Analyze profit potential by selling at nearby mandis."""
    results = []
    
    for mandi in nearby_mandis:
        # Estimate transport cost for 1 unit (kg)
        transport_cost_per_kg = TRANSPORT_COST_PER_KM_PER_KG * mandi['distance_km']
        
        # For now, use placeholder selling prices (in real scenario, fetch from commodity_price.csv)
        sell_prices = {
            'Paddy': {'Palladam': 34, 'Pollachi': 25, 'Udumalpet': 20, 'Madathukulam': 22, 'Coimbatore': 30},
            'Maize': {'Palladam': 24, 'Udumalpet': 21, 'Pollachi': 20, 'Coimbatore': 22},
            'Cotton': {'Palladam': 55, 'Coimbatore': 50},
            'Drumstick': {'Pollachi': 28, 'Coimbatore': 25},
            'Coconut': {'Kinathukadavu': 18, 'Coimbatore': 20},
        }
        
        sell_price = sell_prices.get(crop_name, {}).get(mandi['name'], buy_price + 5)
        
        profit_margin = calculate_profit_margin(sell_price, buy_price, transport_cost_per_kg)
        total_profit_per_kg = sell_price - buy_price - transport_cost_per_kg
        
        results.append({
            'mandi': mandi['name'],
            'distance_km': mandi['distance_km'],
            'state': mandi['state'],
            'sell_price_per_kg': sell_price,
            'transport_cost_per_kg': round(transport_cost_per_kg, 2),
            'profit_per_kg': round(total_profit_per_kg, 2),
            'profit_margin_percent': round(profit_margin, 2),
            'profit_for_100kg': round(total_profit_per_kg * MIN_SHIPMENT_SIZE, 2),
        })
    
    return sorted(results, key=lambda x: x['profit_per_kg'], reverse=True)


def get_mandi_recommendations(user_lat, user_lon, crop_name, cost_price):
    """
    Get mandi recommendations with high profit potential.
    
    Args:
        user_lat: User's latitude (Coimbatore ~11.01)
        user_lon: User's longitude (Coimbatore ~76.66)
        crop_name: Name of crop (e.g., 'Paddy', 'Maize')
        cost_price: Cost price per kg
    
    Returns:
        Dictionary with nearby mandis and profit analysis
    """
    nearby = find_nearby_mandis(user_lat, user_lon, max_distance_km=100)
    profit_analysis = analyze_crop_profit(crop_name, cost_price, nearby)
    
    return {
        'crop': crop_name,
        'cost_price_per_kg': cost_price,
        'analysis_date': datetime.now().isoformat(),
        'nearby_mandis_count': len(nearby),
        'profit_analysis': profit_analysis[:5],  # Top 5 mandis by profit
        'summary': {
            'best_mandi': profit_analysis[0] if profit_analysis else None,
            'avg_transport_cost': round(sum(m['transport_cost_per_kg'] for m in profit_analysis) / len(profit_analysis), 2) if profit_analysis else 0,
            'max_profit_per_kg': round(max(m['profit_per_kg'] for m in profit_analysis), 2) if profit_analysis else 0,
        }
    }


def format_mandi_report(recommendations):
    """Format mandi recommendations as human-readable report."""
    report = []
    report.append(f"\n{'='*70}")
    report.append(f"MANDI PROFITABILITY ANALYSIS - {recommendations['crop'].upper()}")
    report.append(f"{'='*70}")
    report.append(f"Cost Price: Rs {recommendations['cost_price_per_kg']}/kg")
    report.append(f"Analysis Date: {recommendations['analysis_date'][:10]}")
    report.append("")
    
    report.append(f"{'MANDI':<20} {'DIST(km)':<12} {'SELL PRICE':<12} {'TRANSPORT':<12} {'PROFIT/kg':<12} {'MARGIN %':<12}")
    report.append(f"{'-'*70}")
    
    for mandi in recommendations['profit_analysis']:
        report.append(
            f"{mandi['mandi']:<20} "
            f"{mandi['distance_km']:<12.1f} "
            f"Rs {mandi['sell_price_per_kg']:<11} "
            f"Rs {mandi['transport_cost_per_kg']:<11.2f} "
            f"Rs {mandi['profit_per_kg']:<11.2f} "
            f"{mandi['profit_margin_percent']:<11.1f}%"
        )
    
    report.append("")
    report.append(f"{'='*70}")
    report.append("SUMMARY:")
    if recommendations['summary']['best_mandi']:
        best = recommendations['summary']['best_mandi']
        report.append(f"✓ Best Mandi: {best['mandi']} ({best['distance_km']} km away)")
        report.append(f"  - Profit per kg: Rs {best['profit_per_kg']}")
        report.append(f"  - Total profit for 100kg: Rs {best['profit_for_100kg']}")
        report.append(f"  - Profit margin: {best['profit_margin_percent']}%")
    report.append(f"✓ Average Transport Cost: Rs {recommendations['summary']['avg_transport_cost']}/kg")
    report.append(f"✓ Maximum Profit Potential: Rs {recommendations['summary']['max_profit_per_kg']}/kg")
    report.append(f"{'='*70}\n")
    
    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Coimbatore coordinates
    coimbatore_lat = 11.0083
    coimbatore_lon = 76.6551
    
    # Example: Analyze Paddy prices
    recommendations = get_mandi_recommendations(
        coimbatore_lat, coimbatore_lon,
        crop_name='Paddy',
        cost_price=20.0
    )
    
    print(format_mandi_report(recommendations))
    print("\nJSON Response:")
    print(json.dumps(recommendations, indent=2))
