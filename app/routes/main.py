from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Service, CivicIssue, Goal
from app.services.ai_service import get_skhokho_response
from PIL import Image
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/api/map-data')
@login_required
def map_data():
    # Get all services with valid lat/lng
    services = []
    all_services = Service.query.all()
    for service in all_services:
        if service.latitude and service.longitude:
            services.append({
                'id': service.id,
                'lat': service.latitude,
                'lng': service.longitude,
                'title': service.name,
                'type': 'service',
                'category': service.category,
                'price': service.price
            })
    
    # Get all civic issues with valid lat/lng
    issues = []
    all_issues = CivicIssue.query.all()
    for issue in all_issues:
        if issue.latitude and issue.longitude:
            issues.append({
                'id': issue.id,
                'lat': issue.latitude,
                'lng': issue.longitude,
                'title': issue.title,
                'type': 'issue',
                'severity': issue.ai_severity_score,
                'status': issue.city_status
            })
    
    return jsonify({'services': services, 'issues': issues})

@main_bp.route('/home')
@login_required
def home():
    # 1. Greeting Logic
    hour = datetime.now().hour
    if hour < 12: greeting = "Good Morning"
    elif hour < 18: greeting = "Good Afternoon"
    else: greeting = "Good Evening"

    # 2. Mock External Data (This stops the 'weather is undefined' error)
    weather_data = {
        'location': 'SOWETO', 
        'temperature': 24, 
        'description': 'Sunny'
    }
    power_data = {
        'stage': 0, 
        'status': 'Online'
    }
    
    # 3. Wallet & Reputation Data (Universal across all pillars)
    wallet_balance = current_user.wallet_balance
    reputation_points = current_user.reputation_points

    # 4. Get goals from database
    goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).all()

    # 5. Render
    return render_template('index.html', 
                         goals=goals,
                         ticket_count=0,
                         contact_count=0,
                         greeting=greeting,
                         weather=weather_data,
                         power=power_data,
                         wallet_balance=wallet_balance,
                         reputation_points=reputation_points)

@main_bp.route('/location/scan', methods=['POST'])
@login_required
def scan_location():
    """Scan location for nearby services and opportunities"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Location required'}), 400
        
        # Find nearby services (within ~1km)
        nearby_services = Service.query.filter(
            Service.latitude.between(latitude - 0.01, latitude + 0.01),
            Service.longitude.between(longitude - 0.01, longitude + 0.01)
        ).limit(5).all()
        
        findings = []
        for service in nearby_services:
            findings.append(f"📍 FOUND: {service.name} ({service.category}) - R{service.price}")
        
        advice = "Sharp! I found some opportunities nearby. Check LinkUp for more details."
        if not findings:
            advice = "No services detected in this area. Try expanding your search radius."
        
        return jsonify({
            'findings': findings,
            'advice': advice,
            'count': len(findings)
        })
        
    except Exception as e:
        print(f"⚠️ Scan Error: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/analyze/image', methods=['POST'])
@login_required
def analyze_image():
    """Analyze uploaded image with AI vision"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save image temporarily
        from flask import current_app
        filename = secure_filename(f"analysis_{current_user.id}_{int(datetime.now().timestamp())}.jpg")
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Analyze with AI
        image = Image.open(filepath)
        analysis = get_skhokho_response("", "", image=image)
        
        return jsonify({
            'analysis': analysis,
            'image_url': f"/static/uploads/{filename}"
        })
        
    except Exception as e:
        print(f"⚠️ Analysis Error: {e}")
        return jsonify({'error': str(e)}), 500
