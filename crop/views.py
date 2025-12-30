import os
import json
import base64
import mimetypes
import uuid
import logging
import numpy as np
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import tensorflow as tf
from crop.services.weather_api import get_weather
import google.generativeai as genai
from .gemini_ai import ask_gemini







# Supabase client is provided by `crop/utils/supabase_client.py` and imported below

image = tf.keras.preprocessing.image

# Supabase client
from .utils.supabase_client import supabase

logger = logging.getLogger(__name__)

# -------------------- PATHS --------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'crop', 'ml', 'crop_disease_model_single_input.h5')
CLASS_NAMES_PATH = os.path.join(BASE_DIR, 'crop', 'ml', 'class_names.json')

# -------------------- LOAD MODEL --------------------
model = tf.keras.models.load_model(MODEL_PATH)

# -------------------- LOAD CLASS NAMES --------------------
with open(CLASS_NAMES_PATH) as f:
    class_names = json.load(f)

IMG_SIZE = 224

# -------------------- VIEWS --------------------
def home(request):
    return render(request, 'crop/home.html')
# def home(request):
#     return render(request, 'crop/predict.html')


def predict_image(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']

        # ---- FILENAME ----
        orig_name = img_file.name
        ext = os.path.splitext(orig_name)[1] or '.jpg'
        unique_name = f"{uuid.uuid4().hex}{ext}"

        # ---- TEMP SAVE ----
        img_bytes = img_file.read()
        img_path = os.path.join(BASE_DIR, 'crop', 'ml', unique_name)

        with open(img_path, 'wb') as f:
            f.write(img_bytes)

        # ---- PREPROCESS ----
        try:
            img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
            img_array = np.expand_dims(image.img_to_array(img) / 255.0, axis=0)

        except Exception as e:
            context["error"] = f"Image processing error: {e}"
            os.remove(img_path)
            return render(request, 'crop/disease_predict.html', context)

        # ---- PREDICT ----
        try:
            preds = model.predict(img_array)
            idx = int(np.argmax(preds))
            predicted_label = class_names[idx]
            confidence = float(preds[0][idx] * 100)

        except Exception as e:
            context["error"] = f"Prediction failed: {e}"
            predicted_label = None

        # ---- BASE64 FOR DISPLAY ----
        mime_type = mimetypes.guess_type(img_path)[0] or "image/jpeg"
        b64 = base64.b64encode(img_bytes).decode()
        data_uri = f"data:{mime_type};base64,{b64}"

        # ---- UPLOAD TO SUPABASE ----
        bucket = "image"
        storage_path = f"uploads/{unique_name}"
        public_url = None

        try:
            supabase.storage.from_(bucket).upload(
                path=storage_path,
                file=img_bytes,
                file_options={"content-type": mime_type}
            )

            # Public URL
            public_url = supabase.storage.from_(bucket).get_public_url(storage_path)

        except Exception as e:
            logger.warning(f"Supabase upload failed: {e}")

        # ---- INSERT INTO DATABASE ----
        try:
            record = {
                "filename": unique_name,
                "original_filename": orig_name,
                "storage_path": storage_path,
                "image_url": public_url,
                "predicted_disease": predicted_label,
                "confidence": confidence,
                "crop_name": "Unknown",
                "created_at": timezone.now().isoformat()
            }

            supabase.table("plant_disease_analysis").insert(record).execute()

        except Exception as e:
            logger.warning(f"DB insert failed: {e}")

        # UI DISPLAY
        context["predicted_label"] = predicted_label
        context["confidence"] = f"{confidence:.2f}%"
        context["uploaded_image"] = data_uri

        # Delete temp file
        try:
            os.remove(img_path)
        except:
            pass

    return render(request, 'crop/disease_predict.html', context)


def predictions_admin(request):
    try:
        res = supabase.table("plant_disease_analysis") \
                      .select("*") \
                      .order("created_at", desc=True) \
                      .limit(200) \
                      .execute()

        records = res.data or []
    except Exception as e:
        return render(request, "crop/predictions_list.html", {"error": str(e)})

    return render(request, "crop/predictions_list.html", {"records": records})


def prediction_detail(request, filename):
    try:
        res = supabase.table("plant_disease_analysis").select("*").eq("filename", filename).execute()
        record = res.data[0] if res.data else None
    except Exception as e:
        record = None

    return render(request, "crop/prediction_detail.html", {"record": record})
@csrf_exempt

def get_treatment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        disease_name = payload.get("disease_name")
        confidence = payload.get("confidence")

        if not disease_name:
            return JsonResponse({"error": "disease_name required"}, status=400)

        # 🔹 Gemini prompt (STRICT FORMAT)
        prompt = f"""
You are an agriculture expert.

Give SIMPLE organic treatment for farmers.
No bullets. No markdown. No explanation.

Disease: {disease_name}

Format EXACTLY like this:

Organic solution:
Dosage:
Instructions:
Precautions:
"""

        text = ask_gemini(prompt)

        # 🔹 Parse Gemini output safely
        result = {
            "organic_solution": "",
            "dosage": "",
            "instructions": "",
            "precautions": ""
        }

        for line in text.splitlines():
            line = line.strip()
            if line.lower().startswith("organic"):
                result["organic_solution"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("dosage"):
                result["dosage"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("instructions"):
                result["instructions"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("precautions"):
                result["precautions"] = line.split(":", 1)[-1].strip()

        return JsonResponse({
            "disease": disease_name.replace("___", " - ").replace("_", " "),
            "confidence": confidence,
            "found": True,                     # 🔴 IMPORTANT (fixes undefined)
            "organic_solution": result["organic_solution"],
            "dosage": result["dosage"],
            "instructions": result["instructions"],
            "precautions": result["precautions"],
            "source": "gemini"
        }, status=200)

    except Exception as e:
        print("TREATMENT ERROR:", e)
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt  # disable CSRF for API (or handle token in frontend)

def get_crop_schemes(request):
    try:
        # Optional: fetch by category if POST payload contains it
        category = None
        if request.method == 'POST':
            import json
            payload = json.loads(request.body)
            category = payload.get('category', None)

        query = supabase.table('crop_scheme').select('*')
        if category:
            query = query.eq('category', category)

        resp = query.execute()
        data = resp.data if hasattr(resp, 'data') else resp

        if not data:
            return JsonResponse({
                'found': False,
                'message': 'No crop schemes found.'
            }, status=200)

        # Format the data as a list of dicts
        schemes_list = []
        for item in data:
            schemes_list.append({
                'name': item.get('name'),
                'slug': item.get('slug'),
                'category': item.get('category'),
                'max_benefit': item.get('max_benefit'),
                'eligibility_short': item.get('eligibility_short'),
                'key_benefits': item.get('key_benefits'),
                'documents': item.get('documents'),
                'process_steps': item.get('process_steps'),
                'icon': item.get('icon'),
                'link': item.get('link'),
                'farmer_types': item.get('farmer_types'),
                'states': item.get('states'),
                'land_range': item.get('land_range')
            })

        return JsonResponse({
            'found': True,
            'schemes': schemes_list
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def schemes_page(request):
    try:
        # Fetch all crop schemes from Supabase
        resp = supabase.table('crop_scheme').select('*').execute()
        schemes = resp.data if hasattr(resp, 'data') else resp

        return render(request, 'crop/schemes.html', {'schemes': schemes})

    except Exception as e:
        return render(request, 'crop/schemes.html', {'schemes': [], 'error': str(e)})
    
# from django.shortcuts import render
# from django.http import JsonResponse
# from .services.weed_predict import predict_weed, get_model_info
# from .services.opeanai_service import recommend_crop
# from .services.weather_api import get_weather


# def weed_crop_suggestion(request):
#     """Upload image -> detect weed (fallback to crop model if weed model fails) -> (optional) get weather -> ask OpenAI for crop suggestion.
    
#     Also saves the prediction and suggestion to Supabase.

#     POST fields:
#     - weed_image: file
#     - lat (optional), lon (optional): floats for weather lookup
#     - season (optional): string
#     """
#     if request.method != 'POST':
#         return JsonResponse({"error": "Please send a POST request with an image."}, status=400)

#     if not request.FILES.get('weed_image'):
#         return JsonResponse({"error": "Field 'weed_image' is required."}, status=400)

#     weed_image = request.FILES['weed_image']

#     # Save image temporarily in project's temp folder
#     temp_dir = os.path.join(BASE_DIR, 'temp')
#     os.makedirs(temp_dir, exist_ok=True)
#     unique_name = f"weed_{uuid.uuid4().hex}{os.path.splitext(weed_image.name)[1] or '.jpg'}"
#     img_path = os.path.join(temp_dir, unique_name)
#     with open(img_path, 'wb') as f:
#         for chunk in weed_image.chunks():
#             f.write(chunk)

#     try:
#         label, preds = predict_weed(img_path)
#         # derive confidence if preds available
#         try:
#             # preds expected shape (1, n)
#             conf_val = float(preds[0].max()) * 100
#             confidence = f"{conf_val:.2f}%"
#         except Exception:
#             confidence = None

#         # optional weather
#         lat = request.POST.get('lat') or request.GET.get('lat')
#         lon = request.POST.get('lon') or request.GET.get('lon')
#         season = request.POST.get('season') or request.GET.get('season')
#         weather = None
#         if lat and lon:
#             try:
#                 weather = get_weather(lat, lon)
#             except Exception as e:
#                 # non-fatal, continue without weather
#                 weather = None

#         # Ask OpenAI for crop suggestions
#         prompt_extra = "Provide seasonal and weather-based considerations and recommended practices." \
#                        if not season and not weather else None
#         suggestion = recommend_crop(label, weather=weather, season=season, extra_instructions=prompt_extra)

#         # Try to save prediction and suggestion to Supabase
#         try:
#             from .utils.supabase_client import supabase
#             storage_path = f"weed_uploads/{unique_name}"
#             public_url = None
            
#             # Try upload to Supabase storage
#             try:
#                 bucket_name = 'images'
#                 with open(img_path, 'rb') as f:
#                     supabase.storage.from_(bucket_name).upload(storage_path, f.read())
#                 try:
#                     pu = supabase.storage.from_(bucket_name).get_public_url(storage_path)
#                     if isinstance(pu, dict):
#                         public_url = pu.get('publicURL') or pu.get('public_url')
#                     else:
#                         public_url = getattr(pu, 'publicURL', None) or getattr(pu, 'public_url', None) or pu
#                 except Exception:
#                     pass
#             except Exception as e:
#                 logger.warning('Supabase storage upload failed: %s', e)

#             # Insert record into weed_predictions table
#             try:
#                 record = {
#                     'filename': unique_name,
#                     'original_name': weed_image.name,
#                     'weed_detected': label,
#                     'confidence': float(confidence.rstrip('%')) if confidence else None,
#                     'suggestion': suggestion,
#                     'weather': str(weather) if weather else None,
#                     'season': season,
#                     'storage_path': storage_path,
#                     'public_url': public_url,
#                     'created_at': timezone.now().isoformat(),
#                 }
#                 supabase.table('weed_predictions').insert(record).execute()
#             except Exception as e:
#                 logger.warning('Failed to insert weed prediction record into Supabase: %s', e)
#         except Exception as e:
#             logger.warning('Supabase operations failed (non-fatal): %s', e)

#         # If caller requested output-only, return plain text suggestion
#         output_only = (request.POST.get('output_only') or request.GET.get('output_only') or '').lower()
#         if output_only in ('1', 'true', 'yes'):
#             return HttpResponse(suggestion, content_type='text/plain')

#         # include which model was used (and whether fallback)
#         try:
#             model_info = get_model_info()
#         except Exception:
#             model_info = None

#         resp = {
#             'weed_detected': label,
#             'confidence': confidence,
#             'crop_suggestion': suggestion,
#             'model_used': model_info,
#         }
#         return JsonResponse(resp)
#     finally:
#         # cleanup temp file
#         try:
#             os.remove(img_path)
#         except OSError:
#             pass


# def weed_suggestion_ui(request):
#     """Render a small web UI to upload an image and show weed detection + crop suggestion.

#     The UI sends the file via AJAX to the existing `/weed-suggestion/` endpoint and
#     displays the returned JSON (or plain text when `output_only=1` is used).
#     """
#     return render(request, 'crop/weed_suggestion.html')


# def weed_model_diagnostic(request):
#     """Diagnostic endpoint to test if weed model loads and can make a prediction.

#     Returns JSON with model info and test result.
#     """
#     from crop.services.weed_predict import get_model, WEED_CLASSES

#     result = {
#         'status': 'ok',
#         'weed_classes': WEED_CLASSES,
#         'model': None,
#         'errors': [],
#     }

#     # Try to load the model
#     try:
#         model = get_model()
#         result['model'] = {
#             'name': model.name,
#             'input_shape': str(model.input_shape) if hasattr(model, 'input_shape') else 'unknown',
#             'output_shape': str(model.output_shape) if hasattr(model, 'output_shape') else 'unknown',
#         }
#     except Exception as e:
#         result['status'] = 'error'
#         result['errors'].append(f'Model load failed: {e}')

#     # Try a test prediction (dummy input)
#     try:
#         if result['model']:
#             test_input = np.zeros((1, 224, 224, 3), dtype=np.float32)
#             preds = model.predict(test_input, verbose=0)
#             result['test_prediction'] = {
#                 'input_shape': str(test_input.shape),
#                 'output_shape': str(preds.shape),
#                 'output_sample': preds[0].tolist() if len(preds) > 0 else [],
#             }
#     except Exception as e:
#         result['status'] = 'error'
#         result['errors'].append(f'Test prediction failed: {e}')

#     return JsonResponse(result)

    # return JsonResponse(result)
def weather_risk_view(request):
    return HttpResponse("Weather risk feature coming soon!")
from django.shortcuts import render
from .mandi_service import get_best_mandi

# def mandi_form_view(request):
#     result = None
#     if request.method == "POST":
#         crop = request.POST.get("crop")
#         quantity = int(request.POST.get("quantity", 0))
#         transport = request.POST.get("transport")
#         result = get_best_mandi(crop, quantity, transport)
    
#     return render(request, "crop/mandi_form.html", {"result": result})
# from django.shortcuts import render
# from datetime import datetime

# # Dummy market data for demonstration

# MARKETS = [
# {"name": "Wholesale Mandi (New)", "location": "Indore", "distance": 65, "modal_price": 3210, "min_price": 2889, "max_price": 3531, "updated": "52 min"},
# {"name": "Krishi Upaj Mandi (Main)", "location": "Jabalpur", "distance": 16, "modal_price": 3132, "min_price": 2819, "max_price": 3445, "updated": "31 min"},
# {"name": "Local Mandi", "location": "Bhopal", "distance": 40, "modal_price": 3180, "min_price": 2900, "max_price": 3500, "updated": "1 hr"},
# ]

# # Transport cost per km

# TRANSPORT_COST = {
# "Truck": 8,
# "Bike": 4,
# "Cart": 2,
# }

# def find_markets(request):
#     results = []
#     crop = ""
#     quantity = 0
#     transport = ""

#     if request.method == "POST":
#         crop = request.POST.get("crop")
#         district = request.POST.get("district")
#         quantity = float(request.POST.get("quantity", 0))
#         transport = request.POST.get("transport")

#         cost_per_km = TRANSPORT_COST.get(transport, 0)

#         for market in MARKETS:
#             revenue = quantity * market["modal_price"]
#             travel_cost = 2 * market["distance"] * cost_per_km
#             profit = revenue - travel_cost

#             market_data = {
#                 **market,
#                 "revenue": revenue,
#                 "travel_cost": travel_cost,
#                 "profit": profit,
#             }
#             results.append(market_data)

#         # Sort markets by profit descending
#         results = sorted(results, key=lambda x: x["profit"], reverse=True)

#     return render(request, "mandi_form.html", {
#         "results": results,
#         "crop": crop,
#         "quantity": quantity,
#         "transport": transport,
#     })





def weed_upload_page(request):
    return render(request, 'crop/weed_upload.html')
def weed_crop_suggestion(request):
    return render(request, 'crop/weed_upload.html')
# from .models import Scheme

# def schemes_page(request):
#     language = request.GET.get('lang', 'en')
#     schemes = Scheme.objects.all()
#     return render(request, 'schemes.html', {'schemes': schemes, 'language': language})
import math
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services.weather_api import get_weather
# from .services.disease_risk import check_disease_risk
from .utils.weather import fetch_weather

# Distance helper
def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Initial page render
def weather_mandi_view(request):
    lat, lon = 11.0174, 76.9553  # default coordinates
    weather = fetch_weather(lat, lon)
    # risks = check_disease_risk(weather)
    return render(request, "crop/mandi_form.html", {
        "weather": weather,
        "risks": []
    })

# # AJAX: fetch weather and disease dynamically
def get_weather_api(request):
    lat = float(request.GET.get('lat', 11.0174))
    lon = float(request.GET.get('lon', 76.9553))
    weather = fetch_weather(lat, lon)
    # risks = check_disease_risk(weather)
    dummy_risks = [{
        "crop": "N/A",
        "disease": "Feature disabled",
        "precaution": "Disease risk feature is currently unavailable."
    }]
    return JsonResponse({**weather, "risks": dummy_risks})
MANDI_DATA = [
    {"name": "Kalapatti Mandhi", "lat": 11.02, "lon": 76.96},
    {"name": "Podanur Mandhi B", "lat": 11.01, "lon": 76.95},
    {"name": "Somanur Mandhi", "lat": 11.03, "lon": 76.97},
]
# AJAX: mandi recommendation
@csrf_exempt
def mandi_recommendation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_lat = float(data.get("lat", 11.0174))
        user_lon = float(data.get("lon", 76.9553))
        crop = data.get("crop", "Not provided")
        quantity = float(data.get("quantity", 1))

        nearest = []
        for i, m in enumerate(MANDI_DATA):
            dist = distance(user_lat, user_lon, m["lat"], m["lon"])
            nearest.append({
                "market_name": m["name"],
                "location": f"{m['lat']}, {m['lon']}",
                "distance": round(dist, 2)
            })

        # Dummy prices
        price_list = {m["market_name"]: 30 + i*2 for i, m in enumerate(nearest)}

        # Calculate revenue, travel cost, and profit
        result = []
        for m in nearest:
            modal_price = price_list[m["market_name"]]
            revenue = modal_price * quantity
            travel_cost = m["distance"] * 10
            profit = revenue - travel_cost
            result.append({
                **m,
                "modal_price": modal_price,
                "min_price": modal_price - 3,
                "max_price": modal_price + 2,
                "revenue": round(revenue, 2),
                "travel_cost": round(travel_cost, 2),
                "profit": round(profit, 2)
            })

        result = sorted(result, key=lambda x: x["profit"], reverse=True)
        return JsonResponse({"result": result, "crop": crop, "quantity": quantity})

    return JsonResponse({"error": "Invalid request"}, status=400)
# 
from django.shortcuts import render
from .services.weed_predict import detect_weed
from .services.weather_api import fetch_weather
from .utils.mandi_utils import infer_soil_from_weed, recommend_crops
from .utils.gemini_ai import generate_explanation
from django.core.files.storage import FileSystemStorage

def crop_recommendation_view(request):
    return render(request, "crop/weed_upload.html")

def analyze_crop_view(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        lat = float(request.POST.get("lat"))
        lon = float(request.POST.get("lon"))
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)

        # 1. Weed detection
        weed_name, confidence = detect_weed(image)

        # 2. Infer soil & field condition
        soil_info = infer_soil_from_weed(weed_name)

        # 3. Fetch weather
        weather = fetch_weather(lat, lon)

        # 4. Crop recommendation
        recommendations, avoided = recommend_crops(soil_info, weather)

        # 5. Gemini explanation
        explanation = generate_explanation(
            weed_name, soil_info, weather, recommendations, avoided
        )

        return render(request, "crop/predict.html", {
            "weed": weed_name,
            "confidence": confidence,
            "soil": soil_info,
            "weather": weather,
            "recommendations": recommendations,
            "avoided": avoided,
            "explanation": explanation
        })

import json
from django.http import JsonResponse
from .gemini_ai import ask_gemini
@csrf_exempt
def chatbot(request):
    data = json.loads(request.body)

    prompt = f"""
You are an agriculture assistant for Indian farmers.
Rules:
- Automatically reply in the user's language (Tamil or English).
- Use very simple words.
- Keep answers short.
- Use bullet points.
- Avoid long paragraphs.
- Focus only on useful information.

Farmer profile:
State: {data.get("state")}
Land: {data.get("land")} hectares
Farmer Type: {data.get("farmerType")}

User question:
"{data.get("message")}"

Answer in simple language and suggest suitable government schemes.
"""

    reply = ask_gemini(prompt)
    return JsonResponse({"reply": reply})

@csrf_exempt
def best_scheme(request):
    data = json.loads(request.body)

    prompt = f"""
Suggest the best 2 government schemes for this farmer.
Use simple language and bullet points.

State: {data['state']}
Land: {data['land']} acres
Farmer type: {data['farmerType']}
"""

    reply = ask_gemini(prompt)
    return JsonResponse({"reply": reply})
@csrf_exempt
def ask_scheme(request):
    data = json.loads(request.body)

    prompt = f"""
Explain the scheme {data['scheme']} simply.
Use short bullet points.
Language: same as user.
"""

    reply = ask_gemini(prompt)
    return JsonResponse({"reply": reply})
