# update_mandi.py
import requests
import os
from supabase import create_client
import time
from datetime import datetime
from dotenv import load_dotenv
import csv

# Load .env
DOTENV_PATH = r"C:\Users\Keerthi\Downloads\agrisakthi\.env"
if not os.path.exists(DOTENV_PATH):
    raise FileNotFoundError(f".env file not found at {DOTENV_PATH}")
load_dotenv(DOTENV_PATH)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Service Key for insert/update

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Service Key not found in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
lat_lon_map = {
    "Gujarat_Amreli_Damnagar": (21.585, 71.230),
    "Gujarat_Amreli_Savarkundla": (21.564, 71.264),
    "Gujarat_Anand_Khambhat(Grain Market)": (22.307, 72.618),
    "Gujarat_Anand_Khambhat(Grain Market)_Paddy(Dhan)(Common)": (22.307, 72.618),
    "Gujarat_Banaskanth_Vadgam": (24.235, 72.616),
    "Gujarat_Bharuch_Jambusar(Kaavi)": (21.679, 73.050),
    "Gujarat_Gandhinagar_Mansa(Manas Veg Yard)": (23.220, 72.680),
    "Gujarat_Junagarh_Mangrol": (21.510, 70.200),
    "Gujarat_Navsari_Bilimora": (20.780, 72.940),
    "Gujarat_Rajkot_Dhoraji": (21.520, 70.450),
    "Gujarat_Rajkot_Rajkot(Veg.Sub Yard)": (22.303, 70.802),
    "Gujarat_Sabarkantha_Modasa(Tintoi)": (23.600, 73.633),
    "Gujarat_Surat_Mahuva(Anaval)": (21.097, 72.658),
    "Gujarat_Surat_Surat": (21.170, 72.831),
    "Gujarat_Surendranagar_Dhragradhra": (22.971, 71.626),
    "Gujarat_Surendranagar_Vadhvan": (22.981, 71.647),
    "Gujarat_Vadodara(Baroda)_Padra": (22.300, 73.150),
    "Haryana_Fatehabad_Fatehabad": (29.520, 75.450),
    "Haryana_Gurgaon_Gurgaon": (28.459, 77.026),
    "Haryana_Hissar_Hansi": (29.097, 75.958),
    "Haryana_Kaithal_Dhand": (29.775, 76.450),
    "Haryana_Mahendragarh-Narnaul_Narnaul": (28.043, 76.160),
    "Haryana_Mewat_FerozpurZirkha(Nagina)": (28.090, 77.100),
    "Haryana_Mewat_Punhana": (28.050, 77.060),
    "Haryana_Mewat_Tauru": (28.210, 77.000),
    "Haryana_Panipat_Panipat": (29.390, 76.970),
    "Haryana_Panipat_Samalkha": (29.490, 77.020),
    "Haryana_Rewari_Kosli": (28.200, 76.620),
    "Haryana_Rohtak_Meham": (28.900, 76.450),
    "Haryana_Sonipat_Ganaur": (29.120, 77.030),
    "Haryana_Sonipat_Gohana": (29.100, 76.830),
    "Haryana_Yamuna Nagar_Radaur": (30.130, 77.080),
    "Haryana_Yamuna Nagar_Sadhaura": (30.130, 77.060),
    "Himachal Pradesh_Chamba_Chamba": (32.550, 76.120),
    "Himachal Pradesh_Hamirpur_Hamirpur": (31.700, 76.520),
    "Himachal Pradesh_Kangra_Dharamshala": (32.220, 76.320),
}

records = supabase.table("mandi_prices").select("*").execute()

# 4️⃣ Update each record with lat/lon if available
for record in records.data:
    key = f"{record['state']}_{record['district']}_{record['market']}"
    if key in lat_lon_map:
        lat, lon = lat_lon_map[key]
        supabase.table("mandi_prices").update({"latitude": lat, "longitude": lon}).eq("id", record["id"]).execute()

        print(f"Updated: {key} -> lat: {lat}, lon: {lon}")
    else:
        print(f"No lat/lon found for: {key}")

print("✅ Lat/lon update complete!")