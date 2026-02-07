from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from src.models.listing_model import Listing, JobRequest, Lead
import random

web_bp = Blueprint('web', __name__)

# --- HELPER: SCATTER PINS IF NO GPS ---
# This ensures pins don't pile up on top of each other if they lack real coordinates
def attach_coordinates(item_list, default_lat=-26.2514, default_lon=27.8967):
    data = []
    for item in item_list:
        item_dict = {}
        # Check if it's a Listing or a JobRequest (they have different fields)
        if hasattr(item, 'to_dict'):
            item_dict = item.to_dict()
        else:
            # Manually build dict for JobRequest if to_dict is missing
            item_dict = {
                'id': item.id,
                'category': item.category,
                'description': item.description,
                'location': item.location,
                'status': getattr(item, 'status', 'open')
            }

        # If latitude is missing or 0, fake it slightly
        lat = getattr(item, 'latitude', None)
        lon = getattr(item, 'longitude', None)
        
        if not lat: 
            # Random scatter 0.01 degrees ~ 1km
            lat = default_lat + (random.uniform(-0.02, 0.02)) 
        if not lon:
            lon = default_lon + (random.uniform(-0.02, 0.02))

        item_dict['lat'] = lat
        item_dict['lon'] = lon
        data.append(item_dict)
    return data

@web_bp.route("/")
def home():
    return render_template("web/home.html")

@web_bp.route("/map")
def map_view():
    # Public Map: Shows all Verified Listings
    listings = Listing.query.filter_by(is_verified=True).all()
    data = attach_coordinates(listings)
    return render_template("web/map_pro.html", listings=data)

@web_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == 'provider':
        # 1. My Listings
        raw_listings = Listing.query.filter_by(provider_id=current_user.id).all()
        # Use simple dictionary logic (database has lat/lon now)
        listings_data = [item.to_dict() for item in raw_listings]
        
        # 2. Open Job Requests
        open_jobs = JobRequest.query.filter_by(status='open').all()
        jobs_data = []
        for job in open_jobs:
            jobs_data.append({
                'category': job.category,
                'description': job.description,
                'lat': job.latitude,  # <--- Read from DB
                'lon': job.longitude  # <--- Read from DB
            })

        # 3. My Leads
        try:
            my_leads = Lead.query.filter_by(provider_id=current_user.id).all()
        except:
            my_leads = []

        return render_template("web/dashboard.html", 
                               user=current_user, 
                               listings=listings_data, 
                               job_opportunities=jobs_data, # <--- Passing it cleanly
                               leads=my_leads)

    # ... (Keep Customer logic same, just remove attach_coordinates calls) ...

    # ---------------------------------------------------------
    # SCENARIO 2: CUSTOMER (See Help & My Request)
    # ---------------------------------------------------------
    elif current_user.role == 'customer':
        # 1. All Verified Providers (Blue Pins - Help)
        all_raw = Listing.query.filter_by(is_verified=True).all()
        all_listings_data = attach_coordinates(all_raw)

        # 2. MY Open Requests (Red Pins - My Location)
        # Customers only see THEIR OWN requests
        my_jobs_raw = JobRequest.query.filter_by(customer_id=current_user.id).order_by(JobRequest.created_at.desc()).all()
        my_jobs_data = attach_coordinates(my_jobs_raw)
        
        return render_template("web/customer_dashboard.html", 
                               user=current_user, 
                               listings=all_listings_data, # Blue
                               jobs=my_jobs_data)          # Red

    # ---------------------------------------------------------
    # SCENARIO 3: ADMIN
    # ---------------------------------------------------------
    elif current_user.role == 'admin':
        return redirect(url_for('admin.admin_panel'))
    
    return redirect(url_for('web.home'))