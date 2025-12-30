import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()  # load .env file

url = os.getenv("SUPABASE_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")
service_key = os.getenv("SUPABASE_SERVICE_KEY")

# check if loaded correctly
print("URL:", url)
print("Anon Key:", anon_key)
print("Service Key:", service_key)

# initialize Supabase client
supabase = create_client(url, service_key)  # use service key for full access
