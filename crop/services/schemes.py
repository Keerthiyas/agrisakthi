# from supabase import create_client

# SUPABASE_URL = "https://YOUR_PROJECT_URL.supabase.co"
# SUPABASE_KEY = "YOUR_ANON_KEY"
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# def fetch_schemes(state=None, crop=None, farmer_type=None):
#     query = supabase.table("schemes").select("*")

#     if state:
#         query = query.eq("state", state)

#     if crop and crop != "All":
#         query = query.eq("crop_type", crop)

#     if farmer_type and farmer_type != "All":
#         query = query.eq("farmer_type", farmer_type)

#     res = query.execute()
#     return res.data
