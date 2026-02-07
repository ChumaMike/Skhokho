from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from src.models.listing_model import db, Listing
from geopy.geocoders import Nominatim
from src.services.ai_service import ai_brain

# Define a NEW Blueprint just for Listings
listings_bp = Blueprint('listings', __name__, url_prefix='/listings')

@listings_bp.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title")
    category = request.form.get("category")
    price = request.form.get("price")
    address = request.form.get("address")

    # Guard Dog
    existing = Listing.query.filter_by(title=title, provider_id=current_user.id).first()
    if existing:
        flash("You already posted this service.", "warning")
        return redirect(url_for("web.dashboard"))
    
    # Geocoding
    lat, lon = -26.2514, 27.8967 # Default Soweto
    try:        
        geolocator = Nominatim(user_agent="linkup_geo_app")
        location = geolocator.geocode(f"{address}, South Africa")
        if location:
            lat, lon = location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding Error: {e}")

    # AI Tagging
    try:
        tags = ai_brain.generate_keywords(title, category)
    except:
        tags = title.lower()

    # Save
    new_listing = Listing(
        title=title, category=category, price=price, 
        contact=current_user.phone_number, address=address,
        provider_id=current_user.id, is_verified=True, rating=5.0,
        latitude=lat, longitude=lon, keywords=tags
    )
    
    db.session.add(new_listing)
    db.session.commit()
    
    flash("Listing created successfully!", "success")
    return redirect(url_for("web.dashboard"))

@listings_bp.route("/edit/<int:listing_id>", methods=["GET", "POST"])
@login_required
def edit(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    
    if listing.provider_id != current_user.id and current_user.role != 'admin':
        flash("Access Denied", "error")
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        listing.title = request.form.get("title")
        listing.category = request.form.get("category")
        listing.price = request.form.get("price")
        listing.address = request.form.get("address")
        db.session.commit()
        flash("Updated!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("web/edit_listing.html", listing=listing)