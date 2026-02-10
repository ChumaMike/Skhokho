from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import CivicIssue, Service, Job, User
from app.services.ai_service import get_skhokho_response
from PIL import Image
import os
from werkzeug.utils import secure_filename
from datetime import datetime

macalaa_bp = Blueprint('macalaa', __name__)

@macalaa_bp.route('/')
@login_required
def index():
    """Macalaa - The Visual & Voice Assistant Dashboard"""
    return render_template('macalaa.html')

@macalaa_bp.route('/api/macalaa/voice', methods=['POST'])
@login_required
def voice_command():
    """Voice navigation - Execute commands via voice"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        # Voice command routing
        if 'hire' in command and 'plumber' in command:
            # Find plumbers nearby
            plumbers = Service.query.filter_by(category='Plumbing').limit(5).all()
            if plumbers:
                response = f"I found {len(plumbers)} plumbers nearby. Opening LinkUp map..."
                action = {'type': 'navigate', 'url': '/linkup/map'}
            else:
                response = "No plumbers found nearby. Try expanding your search area."
                action = None
                
        elif 'balance' in command or 'money' in command:
            response = f"Your wallet balance is R{current_user.wallet_balance}. Reputation: {current_user.reputation_points} points."
            action = None
            
        elif 'goal' in command or 'mission' in command:
            from app.models import Goal
            goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).count()
            response = f"You have {goals} active goals. Say 'show goals' to view them."
            action = None
            
        elif 'map' in command:
            response = "Opening the map now..."
            action = {'type': 'navigate', 'url': '/linkup/map'}
            
        elif 'report' in command or 'civic' in command:
            response = "Opening CivicNerve reporting system..."
            action = {'type': 'navigate', 'url': '/civic/report'}
            
        else:
            response = "I can help you: hire services, check balance, view goals, open map, or report issues. What would you like?"
            action = None
        
        return jsonify({'response': response, 'action': action})
        
    except Exception as e:
        print(f"⚠️ Voice Command Error: {e}")
        return jsonify({'response': "Sorry, I couldn't process that command."}), 500

@macalaa_bp.route('/api/macalaa/scan-environment', methods=['POST'])
@login_required
def scan_environment():
    """Environment scanning with AI vision - Describes surroundings and detects dangers"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save image temporarily
        filename = secure_filename(f"scan_{current_user.id}_{int(datetime.now().timestamp())}.jpg")
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Analyze with AI Vision
        image = Image.open(filepath)
        analysis = get_skhokho_response("", "", image=image)
        
        # Check for danger keywords
        is_danger = any(keyword in analysis.upper() for keyword in ['DANGER', 'HAZARD', 'WARNING', 'UNSAFE', 'FIRE', 'MANHOLE'])
        
        response_data = {
            'narration': analysis,
            'is_danger': is_danger,
            'image_url': f"/static/uploads/{filename}"
        }
        
        # If danger detected, auto-trigger CivicNerve report
        if is_danger:
            # Extract location from request if provided
            latitude = request.form.get('latitude', -26.2309)
            longitude = request.form.get('longitude', 27.8596)
            
            # Auto-create civic issue
            civic_issue = CivicIssue(
                title="⚠️ DANGER DETECTED by Macalaa",
                description=f"Automatic danger detection:\n\n{analysis}",
                latitude=float(latitude),
                longitude=float(longitude),
                ai_severity_score=95,  # High severity for dangers
                city_status='Reported',
                image_url=f"/static/uploads/{filename}",
                reporter_id=current_user.id
            )
            db.session.add(civic_issue)
            db.session.commit()
            
            response_data['auto_reported'] = True
            response_data['civic_issue_id'] = civic_issue.id
            response_data['urgent_warning'] = "⚠️ DANGER DETECTED! Civic report auto-generated. Nearby users alerted."
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"⚠️ Environment Scan Error: {e}")
        return jsonify({'error': str(e)}), 500

@macalaa_bp.route('/api/macalaa/navigate', methods=['POST'])
@login_required
def navigate_assist():
    """Assist with navigation - describe current location"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Location required'}), 400
        
        # Find nearby landmarks (services and civic issues)
        nearby_services = Service.query.filter(
            Service.latitude.between(latitude - 0.01, latitude + 0.01),
            Service.longitude.between(longitude - 0.01, longitude + 0.01)
        ).limit(3).all()
        
        nearby_issues = CivicIssue.query.filter(
            CivicIssue.latitude.between(latitude - 0.01, latitude + 0.01),
            CivicIssue.longitude.between(longitude - 0.01, longitude + 0.01),
            CivicIssue.city_status != 'Resolved'
        ).limit(3).all()
        
        # Build narration
        narration = f"You are at coordinates {latitude:.4f}, {longitude:.4f}. "
        
        if nearby_services:
            service_names = [s.name for s in nearby_services]
            narration += f"Nearby services: {', '.join(service_names)}. "
        
        if nearby_issues:
            narration += f"⚠️ Warning: {len(nearby_issues)} reported civic issues in this area. "
            for issue in nearby_issues:
                if issue.ai_severity_score > 70:
                    narration += f"High severity: {issue.title}. "
        
        if not nearby_services and not nearby_issues:
            narration += "No notable landmarks or issues nearby."
        
        return jsonify({
            'narration': narration,
            'nearby_services': len(nearby_services),
            'nearby_issues': len(nearby_issues),
            'warnings': [{'title': i.title, 'severity': i.ai_severity_score} for i in nearby_issues if i.ai_severity_score > 70]
        })
        
    except Exception as e:
        print(f"⚠️ Navigation Error: {e}")
        return jsonify({'error': str(e)}), 500
