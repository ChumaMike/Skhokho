import requests
import os
import logging

logger = logging.getLogger(__name__)

def get_weather(location):
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return {'error': 'API Key missing'}

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5) # Enterprise Rule: Always set a timeout!
        data = response.json()

        if response.ok:
            return {
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'location': data['name']
            }
        return {'error': data.get('message', 'Weather fetch failed')}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return {'error': 'Service unavailable'}

def get_daily_quote():
    try:
        response = requests.get("https://api.quotable.io/random", timeout=3)
        data = response.json()
        return f"\"{data['content']}\" — {data['author']}"
    except:
        return "Keep pushing, Skhokho."