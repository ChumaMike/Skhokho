from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.listing_model import db, JobRequest, Listing
from geopy.geocoders import Nominatim
import random

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route("/create", methods=["POST"])
@login_required
def create():
    category = request.form.get("category")
    description = request.form.get("description")
    location_text = request.form.get("location")
    
    # 1. CALCULATE COORDINATES ONCE (The "Freeze" Logic)
    lat, lon = -26.2514, 27.8967 # Default Soweto
    try:
        # Try to find real address
        geolocator = Nominatim(user_agent="linkup_geo_app")
        loc = geolocator.geocode(f"{location_text}, Soweto, South Africa")
        if loc:
            lat = loc.latitude
            lon = loc.longitude
        else:
            # If address not found, Fuzz it slightly ONCE so it doesn't overlap perfectly
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
    except:
        # If internet fails, just fuzz the default
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)

    new_job = JobRequest(
        customer_id=current_user.id,
        category=category,
        description=description,
        location=location_text,
        latitude=lat,   # <--- Saved forever
        longitude=lon   # <--- Saved forever
    )
    db.session.add(new_job)
    db.session.commit()
    
    # 2. Broadcast Logic
    # (Finding providers and simulating WhatsApp)
    potential_matches = Listing.query.filter(Listing.category.ilike(f"%{category}%")).all()
    provider_phones = set(l.contact for l in potential_matches)
    
    print(f"\n📢 --- JOB BROADCAST #{new_job.id} ---")
    if provider_phones:
        for phone in provider_phones:
            print(f"📲 Alerting {phone}: New {category} job in {location}")
        flash(f"Alerted {len(provider_phones)} providers!", "success")
    else:
        flash("Request saved. Waiting for providers.", "warning")
        
    return redirect(url_for("web.dashboard"))