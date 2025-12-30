# insert_market_data.py
from django.core.management.base import BaseCommand
import csv
import os
from supabase import create_client
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Insert market data into Supabase from CSV"

    def handle(self, *args, **kwargs):
        # -------------------------------
        # Load .env from project root
        # -------------------------------
        DOTENV_PATH = r"C:\Users\Keerthi\Downloads\agrisakthi\.env"
        if not os.path.exists(DOTENV_PATH):
            self.stdout.write(self.style.ERROR(f".env file not found at {DOTENV_PATH}"))
            return

        load_dotenv(DOTENV_PATH)
        self.stdout.write(f".env loaded from {DOTENV_PATH}")

        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
        if not SUPABASE_URL or not SUPABASE_KEY:
            self.stdout.write(self.style.ERROR("Supabase URL or Service Key not found in environment variables."))
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # -------------------------------
        # CSV file path (same folder as this command)
        # -------------------------------
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_FILE_PATH = os.path.join(SCRIPT_DIR, "market_data.csv")

        if not os.path.exists(CSV_FILE_PATH):
            self.stdout.write(self.style.ERROR(f"CSV file not found at {CSV_FILE_PATH}"))
            return

        self.stdout.write(f"CSV found at: {CSV_FILE_PATH}")

        # -------------------------------
        # Read CSV and prepare data
        # -------------------------------
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data_list = []

            for row in reader:
                market_name = row.get("market_name")
                crop_name = row.get("crop_name")
                price_per_kg = row.get("price_per_kg")
                latitude = row.get("latitude")
                longitude = row.get("longitude")

                # Skip rows with missing essential data
                if not market_name or not crop_name or not price_per_kg:
                    self.stdout.write(f"Skipping row due to missing data: {row}")
                    continue

                # Convert numeric fields
                try:
                    price_per_kg = float(price_per_kg)
                    latitude = float(latitude)
                    longitude = float(longitude)
                except ValueError:
                    self.stdout.write(f"Skipping row due to invalid number: {row}")
                    continue

                # Check duplicates in Supabase
                existing = supabase.table("market_prices") \
                    .select("id") \
                    .eq("market_name", market_name) \
                    .eq("crop_name", crop_name) \
                    .eq("price_per_kg", price_per_kg) \
                    .execute()

                if existing.data and len(existing.data) > 0:
                    self.stdout.write(f"Skipping duplicate: {crop_name} at {market_name}")
                    continue

                data_list.append({
                    "market_name": market_name,
                    "crop_name": crop_name,
                    "price_per_kg": price_per_kg,
                    "latitude": latitude,
                    "longitude": longitude
                })

        # -------------------------------
        # Insert all new rows at once
        # -------------------------------
        if data_list:
            response = supabase.table("market_prices").insert(data_list).execute()
            if response.get("error"):
                self.stdout.write(self.style.ERROR(f"Error inserting data: {response['error']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Successfully inserted {len(data_list)} rows into Supabase!"))
        else:
            self.stdout.write("No new rows to insert.")
