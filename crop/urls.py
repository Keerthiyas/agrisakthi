from django import views
from django.urls import path
from django.views.generic import RedirectView



from .views import (
auth_view,

dashboard,
get_crop_schemes,
home,
main_chatbot_api,
main_chatbot_page,
predict_image,
predictions_admin,
prediction_detail,
get_treatment,
mandi_recommendation,
schemes_chatbot,
schemes_page,
# get_schemes_api,
weather_mandi_view,
crop_recommendation_view,

best_scheme,
ask_scheme,
get_weather_api,
analyze_crop_view,
logout_view,

)

urlpatterns = [
# Home page
# path('', home, name='home'),
# Prediction routes
path('predict/', predict_image, name='predict'),
path('predictions/', predictions_admin, name='predictions_admin'),
path('predictions/<str:filename>/', prediction_detail, name='prediction_detail'),

# Weed prediction and crop recommendation
# path('weed/predict/', weed_crop_suggestion, name='weed_predict'),
# path('weed/ui/', weed_suggestion_ui, name='weed_suggestion_ui'),
# path('crop-recommendation/', weed_suggestion_ui, name='crop_recommendation'),
# path('weed/diagnostic/', weed_model_diagnostic, name='weed_diagnostic'),
# path("weather-market/", mandi_form_view, name="find_markets"),
path('schemes/', schemes_page, name='schemes_page'),      # HTML page
path('api/crop-schemes/', get_crop_schemes, name='get_crop_schemes'),

path('weather-market/', weather_mandi_view, name='weather_disease'),
path('api/find-markets/', mandi_recommendation, name='find_markets'),
path('get_weather/', get_weather_api, name='get_weather_api'), 
path('crop-recommendation/', crop_recommendation_view, name='crop_recommendation'),
path("crop-recommendation/analyze/", analyze_crop_view, name="analyze_crop"),
# Treatment route
path('treatment/', get_treatment, name='get_treatment'),
path("schemes-chatbot/", schemes_chatbot, name="schemes_chatbot"),
path("best-scheme/", best_scheme),

path("ask-scheme/", ask_scheme),
path('', auth_view, name='auth'),   # Single login/signup page
path('home/', home, name='home'),
path('logout/', logout_view, name='logout'),

path('dashboard/', dashboard, name='dashboard'),
path("chatbot/", main_chatbot_page, name="chatbot_page"), 
path("chatbot-api/", main_chatbot_api, name="chatbot_api"),

# Favicon
path('favicon.ico', RedirectView.as_view(url='/static/crop/images/favicon.ico')),
]
