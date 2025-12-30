# import_mandi_data.py
import csv
import os
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv

# -------------------------------
# Load .env file explicitly
# -------------------------------
DOTENV_PATH = r"C:\Users\Keerthi\Downloads\agrisakthi\.env"
if not os.path.exists(DOTENV_PATH):
    raise FileNotFoundError(f".env file not found at {DOTENV_PATH}")

load_dotenv(DOTENV_PATH)  # Load environment variables

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Use Service Key for insert access

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase URL or Service Key not found in environment variables. "
        "Please check your .env file."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# CSV file path (same folder as this script)
# -------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_NAME = "commodity_price.csv"  # Your CSV file name
CSV_FILE_PATH = os.path.join(SCRIPT_DIR, CSV_FILE_NAME)

if not os.path.exists(CSV_FILE_PATH):
    raise FileNotFoundError(f"CSV file not found at {CSV_FILE_PATH}")

# -------------------------------
# Helper function to safely convert to int
# -------------------------------
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

# -------------------------------
# Import CSV data into Supabase
# -------------------------------
with open(CSV_FILE_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            # Map CSV headers
            state = row.get("State")
            district = row.get("District")
            market = row.get("Market")
            commodity = row.get("Commodity")
            variety = row.get("Variety")
            grade = row.get("Grade")
            arrival_date_raw = row.get("Arrival_Date")
            min_price = to_int(row.get("Min_x0020_Price"))
            max_price = to_int(row.get("Max_x0020_Price"))
            modal_price = to_int(row.get("Modal_x0020_Price"))

            # Skip row if essential data is missing
            if not market or not commodity or not arrival_date_raw:
                print(f"Skipping row due to missing essential data: {row}")
                continue

            # Convert date from DD/MM/YYYY → YYYY-MM-DD
            arrival_date = datetime.strptime(arrival_date_raw, "%d/%m/%Y").date()

            # Check for duplicates in Supabase
            existing = supabase.table("mandi_prices") \
                .select("id") \
                .eq("market", market) \
                .eq("commodity", commodity) \
                .eq("arrival_date", str(arrival_date)) \
                .execute()

            if existing.data and len(existing.data) > 0:
                print(f"Skipping duplicate: {commodity} at {market} on {arrival_date}")
                continue

            # Insert into Supabase
            supabase.table("mandi_prices").insert({
                "state": state,
                "district": district,
                "market": market,
                "commodity": commodity,
                "variety": variety,
                "grade": grade,
                "arrival_date": str(arrival_date),
                "min_price": min_price,
                "max_price": max_price,
                "modal_price": modal_price,
                "source_filename": CSV_FILE_NAME
            }).execute()

            print(f"Inserted: {commodity} at {market} on {arrival_date}")

        except Exception as e:
            print(f"Error processing row: {row}\n{e}")
