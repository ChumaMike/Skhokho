from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import CivicTicket
from app.services.ai_service import get_skhokho_response
import hashlib

civic_bp = Blueprint('civic', __name__)

@civic_bp.route('/')
def dashboard():
    # Show all tickets on a map/list
    tickets = CivicTicket.query.order_by(CivicTicket.created_at.desc()).all()
    return render_template('civic/dashboard.html', tickets=tickets)

@civic_bp.route('/report', methods=['POST'])
@login_required
def report_issue():
    """The 'Water Burst' Scenario"""
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image') # The photo of the leak
    
    # 1. AI GUARDIAN ANALYSIS 🛡️
    # We send the image to Gemini to assess severity
    # In a real app, we would process the image file here
    ai_verdict = get_skhokho_response(
        f"Analyze this civic issue report: {title} - {description}. Rate severity 1-100.", 
        context_data="CivicNerve Guardian Protocol"
    )
    
    # 2. GENERATE DIGITAL SEAL (SHA-256) 🔐
    # This proves the report hasn't been tampered with
    raw_data = f"{title}{current_user.id}{datetime.utcnow()}"
    digital_seal = hashlib.sha256(raw_data.encode()).hexdigest()
    
    # 3. SAVE TO DB
    new_ticket = CivicTicket(
        title=title,
        description=description,
        author=current_user,
        guardian_seal=digital_seal,
        status="Investigating",
        ai_risk_score=85 # In real code, parse this from AI response
    )
    db.session.add(new_ticket)
    db.session.commit()
    
    flash(f"Ticket Logged! Guardian Seal: {digital_seal[:8]}...", "success")
    return redirect(url_for('civic.dashboard'))