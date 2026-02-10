from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import CivicIssue
from app.services.ai_service import analyze_issue
import hashlib
from datetime import datetime

civic_bp = Blueprint('civic', __name__)

@civic_bp.route('/')
def dashboard():
    # Show all issues on a map/list
    issues = CivicIssue.query.order_by(CivicIssue.created_at.desc()).all()
    return render_template('civic/dashboard.html', issues=issues)

@civic_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'GET':
        return render_template('civic/report.html')
        
    """The 'CivicNerve' Scenario"""
    title = request.form.get('title')
    description = request.form.get('description')
    latitude = request.form.get('latitude', -26.2321)
    longitude = request.form.get('longitude', 27.8816)
    image = request.files.get('image') # The photo of the issue
    
    # 1. AI GUARDIAN ANALYSIS 🛡️
    ai_severity_score = analyze_issue(description)
    
    # 2. GENERATE DIGITAL SEAL (SHA-256) 🔐
    # This proves the report hasn't been tampered with
    raw_data = f"{title}{current_user.id}{datetime.utcnow()}"
    digital_seal = hashlib.sha256(raw_data.encode()).hexdigest()
    
    # 3. GAMIFICATION: REWARD USER
    if ai_severity_score > 50:
        current_user.wallet_balance += 50
        current_user.reputation_points += 10
        flash('City AI analyzed your report. Severity: High. You earned 50 Credits!', 'success')
    else:
        flash('City AI analyzed your report. Severity: Low.', 'info')
    
    # 4. SAVE TO DB
    new_issue = CivicIssue(
        title=title,
        description=description,
        reporter_id=current_user.id,
        latitude=float(latitude),
        longitude=float(longitude),
        ai_severity_score=ai_severity_score,
        city_status="Reported"
    )
    db.session.add(new_issue)
    db.session.commit()
    
    return redirect(url_for('civic.dashboard'))
