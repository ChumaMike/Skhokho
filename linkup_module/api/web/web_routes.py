from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
import random

# --- CORRECT IMPORTS ---
# 1. Import LinkUp-specific models from the module folder
from linkup_module.models.listing_model import Listing
# 2. Import App-wide models (like JobRequest) from the main app
from app.models import JobRequest 
# Note: 'Lead' model was not found in your file tree, so I removed it for now 
# to prevent "ImportError". If you have it, add: from app.models import Lead

web_bp = Blueprint('web', __name__)

# --- HELPER: SCATTER PINS ---
def attach_coordinates(item_list, default_lat=-26.2514, default_lon=27.8967):
    data = []
    for item in item_list:
        item_dict = {}
        # Handle objects that have to_dict() vs those that don't
        if hasattr(item, 'to_dict'):
            item_dict = item.to_dict()
        else:
            item_dict = {
                'id': item.id,
                'category': getattr(item, 'category', 'General'),
                'description': getattr(item, 'description', ''),
                'status': getattr(item, 'status', 'open')
            }

        # Safe attribute access for lat/lon
        lat = getattr(item, 'latitude', None)
        lon = getattr(item, 'longitude', None)
        
        if not lat: lat = default_lat + (random.uniform(-0.02, 0.02)) 
        if not lon: lon = default_lon + (random.uniform(-0.02, 0.02))

        item_dict['lat'] = lat
        item_dict['lon'] = lon
        data.append(item_dict)
    return data

@web_bp.route("/")
def home():
    return render_template("web/home.html")

# --- THE FIX IS HERE: Used @web_bp and added the @ symbol ---
@web_bp.route('/map')
def map_view():
    # 1. Fetch Verified Listings
    listings = Listing.query.filter_by(is_verified=True).all()
    
    # 2. Convert to JSON-friendly dicts
    listings_data = [{
        'id': l.id,
        'title': l.title,
        'latitude': l.latitude,
        'longitude': l.longitude,
        'category': l.category
    } for l in listings]

    return render_template('web/map_pro.html', listings=listings_data)

@web_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == 'provider':
        # Provider Logic
        raw_listings = Listing.query.filter_by(provider_id=current_user.id).all()
        listings_data = [l.to_dict() for l in raw_listings]
        
        open_jobs = JobRequest.query.filter_by(status='open').all()
        jobs_data = [{
            'category': j.category,
            'description': j.description,
            'lat': getattr(j, 'latitude', -26.25),
            'lon': getattr(j, 'longitude', 27.89)
        } for j in open_jobs]

        return render_template("web/dashboard.html", 
                               user=current_user, 
                               listings=listings_data, 
                               job_opportunities=jobs_data, 
                               leads=[]) # Empty list for now until Lead model is fixed

    elif current_user.role == 'customer':
        # Customer Logic
        all_raw = Listing.query.filter_by(is_verified=True).all()
        all_listings_data = attach_coordinates(all_raw)

        my_jobs_raw = JobRequest.query.filter_by(customer_id=current_user.id).order_by(JobRequest.created_at.desc()).all()
        my_jobs_data = attach_coordinates(my_jobs_raw)
        
        return render_template("web/customer_dashboard.html", 
                               user=current_user, 
                               listings=all_listings_data,
                               jobs=my_jobs_data)

    return redirect(url_for('web.home'))