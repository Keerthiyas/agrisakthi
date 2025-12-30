#!/usr/bin/env python
"""Test mandi search service with Coimbatore location."""
from crop.mandi_service import find_nearby_mandis, get_crop_list
import json

# Coimbatore coordinates
coimbatore_lat = 11.0083
coimbatore_lon = 76.6551

print('Available crops:')
crops = get_crop_list()
print(f'Total crops: {len(crops)}')
print('Sample:', ', '.join(crops[:5]))

print('\n' + '='*80)
print('NEARBY MANDIS FOR PADDY (50km radius from Coimbatore):')
print('='*80)
mandis = find_nearby_mandis(coimbatore_lat, coimbatore_lon, crop_name='Paddy', radius_km=50, transport_cost_per_km=2.0)
print(f'Found {len(mandis)} mandis\n')
for m in mandis[:5]:
    print(f"Mandi: {m['market_name']}")
    print(f"  Distance: {m['distance_km']}km | Price: Rs {m['price_per_kg']}/kg")
    print(f"  Transport cost: Rs {m['transport_cost_per_km']}/kg | Net Profit: Rs {m['profit_per_kg']}/kg\n")

print('\n' + '='*80)
print('MANDIS WITH HIGHEST PROFIT (All crops):')
print('='*80)
all_mandis = find_nearby_mandis(coimbatore_lat, coimbatore_lon, crop_name=None, radius_km=50, transport_cost_per_km=2.0, max_results=10)
print(f'Found {len(all_mandis)} highest-profit mandis\n')
for m in all_mandis[:10]:
    print(f"{m['market_name']:25} | {m['crop_name']:15} | Price: Rs {m['price_per_kg']:5.0f} | Profit: Rs {m['profit_per_kg']:6.2f}")
