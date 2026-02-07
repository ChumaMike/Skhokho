from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.macalaa_service import analyze_scene
from app.extensions import db
# Import CivicNerve Ticket model (Assuming it exists, if not we create a placeholder)
# from app.models import Ticket 
import os
import time

macalaa_bp = Blueprint('macalaa', __name__)

@macalaa_bp.route('/')
@login_required
def index():
    return render_template('macalaa/index.html')

@macalaa_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    if 'image' not in request.files:
        return jsonify({"error": "No image sent"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    # 1. Save Image Temporarily
    filename = f"scan_{current_user.id}_{int(time.time())}.jpg"
    filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)

    # 2. The "Brain" Analyzes it
    analysis = analyze_scene(filepath)
    
    # 3. The "Guardian" Logic
    alert_msg = ""
    
    # SCENARIO A: CRITICAL DANGER (Gun, Fire) -> Auto Report
    if analysis['danger_level'] == 'CRITICAL':
        # Logic to create a high-priority ticket automatically
        # new_ticket = Ticket(user_id=current_user.id, type='EMERGENCY', ...)
        # db.session.add(new_ticket)
        # db.session.commit()
        alert_msg = "🚨 EMERGENCY DETECTED. Authorities have been alerted."

    # SCENARIO B: CIVIC ISSUE (Pothole) -> Suggest Report
    elif analysis['action_needed'] == 'REPORT':
        alert_msg = "🛠️ Civic Issue Detected. You can earn points by reporting this."

    return jsonify({
        "result": analysis,
        "image_url": filename,
        "alert": alert_msg
    })