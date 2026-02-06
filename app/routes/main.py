from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Goal, CivicTicket

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def home():
    # 1. Calculate Greeting 🌅
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # 2. Get User Data (Goals & Tickets) 🎯
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='Active').limit(3).all()
    
    # 3. Mock Weather & Power Data (Since we removed the external service) 🌦️
    # You can hook this up to a real API later if you want
    weather = {
        'location': 'SOWETO',
        'temperature': 24,
        'description': 'Sunny'
    }
    power = {
        'stage': 0, # Loadshedding Stage
        'status': 'Online'
    }

    # 4. Render the Dashboard
    return render_template(
        'index.html',
        greeting=greeting,
        weather=weather,
        power=power,
        goals=active_goals
    )