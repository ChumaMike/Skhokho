from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user, login_required
from app.services.weather_service import get_current_weather, get_daily_quote
from app.services.eskom_service import get_loadshedding_status
from app.models import Goal, Contact
from datetime import datetime
from flask import request
from PIL import Image
import os


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # 1. Environment Intel (Weather & Power)
    # [cite_start]Defaulting to Soweto since that's your base [cite: 2]
    weather = get_current_weather("Soweto") 
    power = get_loadshedding_status()
    quote = get_daily_quote()
    
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "GOOD MORNING"
    elif 12 <= current_hour < 17:
        greeting = "GOOD AFTERNOON"
    elif 17 <= current_hour < 21:
        greeting = "GOOD EVENING"
    else:
        greeting = "LATE NIGHT OPS"
        
    context = {
        'weather': weather,
        'power': power,
        'quote': quote,
        'greeting': greeting,  # <--- Pass this to the template
        'goals': [],
        'alerts': []
    }
    # 2. User Specific Intel (Only if logged in)
    if current_user.is_authenticated:
        # Fetch Top 3 Active Goals (Sorted by those closest to completion)
        active_goals = Goal.query.filter_by(user_id=current_user.id, is_archived=False).all()
        # Sort in Python to avoid complex SQL for now: 
        # Prioritize high progress but not yet done
        active_goals.sort(key=lambda x: x.progress, reverse=True)
        context['goals'] = active_goals[:3]

        # Fetch Network Alerts (Contacts not seen in > 30 days)
        # In a real app, do this query in SQL for speed. Here, Python is fine for MVP.
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        alerts = []
        now = datetime.utcnow()
        for c in contacts:
            if c.last_contacted:
                days_since = (now - c.last_contacted).days
                if days_since > 30:
                    alerts.append({'name': c.name, 'days': days_since, 'id': c.id})
            else:
                # Never contacted
                alerts.append({'name': c.name, 'days': '∞', 'id': c.id})
        
        context['alerts'] = alerts[:3] # Just top 3 alerts

    return render_template('index.html', **context)

@main_bp.route('/analyze/image', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Open image for Gemini
        image = Image.open(file)
        
        # Send to Skhokho Vision
        from app.services.ai_service import get_skhokho_response
        analysis = get_skhokho_response(user_message="", image=image)
        
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500