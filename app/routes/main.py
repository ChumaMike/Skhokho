from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Goal, CivicTicket, NetworkContact
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
@login_required
def home():
    # 1. Get Data (Safe Queries)
    try:
        active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).limit(3).all()
        ticket_count = CivicTicket.query.filter_by(user_id=current_user.id).count()
        contact_count = NetworkContact.query.filter_by(user_id=current_user.id).count()
    except Exception as e:
        print(f"⚠️ DB Error: {e}")
        active_goals = []
        ticket_count = 0
        contact_count = 0

    # 2. Greeting Logic
    hour = datetime.now().hour
    if hour < 12: greeting = "Good Morning"
    elif hour < 18: greeting = "Good Afternoon"
    else: greeting = "Good Evening"

    # 3. Mock External Data (This stops the 'weather is undefined' error)
    weather_data = {
        'location': 'SOWETO', 
        'temperature': 24, 
        'description': 'Sunny'
    }
    power_data = {
        'stage': 0, 
        'status': 'Online'
    }

    # 4. Render
    return render_template('index.html', 
                         goals=active_goals,
                         ticket_count=ticket_count,
                         contact_count=contact_count,
                         greeting=greeting,
                         weather=weather_data, # ✅ Sending Weather
                         power=power_data)     # ✅ Sending Power