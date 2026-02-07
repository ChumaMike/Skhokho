from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Goal, CivicTicket

main_bp = Blueprint('main', __name__)

# --- 1. THE PUBLIC LANDING PAGE (Unlocked) ---
@main_bp.route('/')
def index():
    # If user is already logged in, send them straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    # Otherwise, show the public sales page
    return render_template('landing.html') # You need a basic landing.html, or reuse login.html

# --- 2. THE PRIVATE DASHBOARD (Locked) ---
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

    # 2. Get User Data (Goals) 🎯
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='Active').limit(3).all()
    
    # 3. Mock Data 🌦️
    weather = {'location': 'SOWETO', 'temperature': 24, 'description': 'Sunny'}
    power = {'stage': 0, 'status': 'Online'}

    # 4. Render Dashboard
    return render_template(
        'index.html',
        greeting=greeting,
        weather=weather,
        power=power,
        goals=active_goals
    )