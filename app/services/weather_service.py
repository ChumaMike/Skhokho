import os
import requests
import random

def get_current_weather(city="Johannesburg"):
    """
    Safely gets weather. Returns Mock Data if API fails or key is missing.
    """
    api_key = os.environ.get("WEATHER_API_KEY")

    # --- PLAN A: REAL API ---
    if api_key:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'city': city
                }
        except Exception as e:
            print(f"⚠️ Weather API Failed: {e}")
    
    # --- PLAN B: FALLBACK ---
    print("⚠️ Using Mock Weather Data")
    return {
        'temperature': 28,
        'description': 'Sunny (Offline Mode)',
        'icon': '01d',
        'city': 'Soweto'
    }

def get_daily_quote():
    """
    Returns a random motivational quote.
    """
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "It always seems impossible until it is done. - Nelson Mandela",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "Code is like humor. When you have to explain it, it’s bad. - Cory House",
        "Fix the cause, not the symptom. - Steve Maguire"
    ]
    return random.choice(quotes)