import streamlit as st
import requests
from langchain_community.chat_models import ChatOllama

# Weather API Configuration
WEATHER_API_KEY = "887f15bff1d34781807164205250403"
WEATHER_API_URL = "http://api.weatherapi.com/v1/forecast.json"

def get_weather_data(location):
    """Fetches weather data for a given location using WeatherAPI."""
    params = {"key": WEATHER_API_KEY, "q": location, "days": 7, "aqi": "no", "alerts": "no"}
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        forecast = data.get("forecast", {}).get("forecastday", [])
        if not forecast:
            return None
        avg_temp = round(sum(day['day']['avgtemp_c'] for day in forecast) / len(forecast), 2)
        total_rainfall = round(sum(day['day']['totalprecip_mm'] for day in forecast), 2)
        avg_humidity = round(sum(day['day']['avghumidity'] for day in forecast) / len(forecast), 2)
        return {'avg_temp': avg_temp, 'total_rainfall': total_rainfall, 'avg_humidity': avg_humidity}
    except requests.exceptions.RequestException as e:
        st.error(f"Weather API Error: {e}")
        return None

def generate_recommendation(crop, planting_period, location, soil_type):
    """Generates a crop planting recommendation."""
    weather_summary = get_weather_data(location)
    if not weather_summary:
        return "Error fetching weather data. Please check your location."
    prompt = f"""
    You are an AI assistant helping farmers optimize their crop planting strategy.
    Crop: {crop}
    Location: {location}
    Soil Type: {soil_type if soil_type else "Not specified"}
    Planting Period: {planting_period}
    Weather Conditions:
    - Avg Temp: {weather_summary['avg_temp']}°C
    - Total Rainfall: {weather_summary['total_rainfall']} mm
    - Avg Humidity: {weather_summary['avg_humidity']}%
    Analyze the conditions and recommend the best approach for successful farming.
    """
    chat_model = ChatOllama(model="gemma2:2b")
    response = chat_model.invoke(prompt)
    return response

# Streamlit UI
st.title("🌱 AI-Powered Crop Recommendation System")

# Input Form
with st.form("crop_form"):
    crop = st.text_input("Enter Crop Name:")
    planting_period = st.text_input("Enter Planting Period (e.g., June-August):")
    location = st.text_input("Enter Location:")
    soil_type = st.text_input("Enter Soil Type (optional):")
    submit_button = st.form_submit_button("Get Recommendation")

if submit_button:
    if crop and planting_period and location:
        recommendation = generate_recommendation(crop, planting_period, location, soil_type)
        st.subheader("Recommendation:")
        st.write(recommendation)
    else:
        st.warning("Please fill in all required fields.")