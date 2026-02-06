from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ProviderProfile, JobRequest, User

linkup_bp = Blueprint('linkup', __name__)

# --- 1. THE MAP (Customer View) ---
@linkup_bp.route('/')
def map_view():
    """Shows all providers on a map"""
    # In a real app, we would filter by location
    providers = ProviderProfile.query.filter_by(is_verified=True).all()
    return render_template('linkup/map.html', providers=providers)

# --- 2. THE DASHBOARD (Provider View) ---
@linkup_bp.route('/dashboard')
@login_required
def provider_dashboard():
    # Check if user IS a provider
    profile = ProviderProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        return render_template('linkup/onboarding.html') # Force them to join
        
    # Get leads/jobs for this provider
    my_leads = JobRequest.query.filter(
        JobRequest.description.contains(profile.service_category)
    ).all()
    
    return render_template('linkup/dashboard.html', profile=profile, leads=my_leads)

# --- 3. ONBOARDING (Join the Economy) ---
@linkup_bp.route('/join', methods=['POST'])
@login_required
def join_economy():
    business_name = request.form.get('business_name')
    category = request.form.get('category') # Plumber, Coder, etc.
    phone = request.form.get('phone')
    
    # Create Profile
    new_profile = ProviderProfile(
        user_id=current_user.id,
        business_name=business_name,
        service_category=category,
        phone_number=phone,
        is_verified=False # Requires Admin approval later
    )
    db.session.add(new_profile)
    
    # Update User Role
    current_user.role = "provider"
    db.session.commit()
    
    flash("Welcome to the Economy! Your profile is live.", "success")
    return redirect(url_for('linkup.provider_dashboard'))