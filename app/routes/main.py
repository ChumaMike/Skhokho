from flask import Blueprint, render_template
from flask_login import current_user
from app.services.weather_service import get_weather, get_daily_quote
from app.services.eskom_service import get_loadshedding_status
from app.models import Goal, Contact
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # 1. Environment Intel (Weather & Power)
    # [cite_start]Defaulting to Soweto since that's your base [cite: 2]
    weather = get_weather("Soweto") 
    power = get_loadshedding_status()
    quote = get_daily_quote()
    
    context = {
        'weather': weather,
        'power': power,
        'quote': quote,
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