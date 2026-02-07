import os
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.models.user_model import User
from src.models.listing_model import Listing, db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 🔒 SECURITY GATE: Checks for the 'is_admin' session stamp
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If the stamp is missing, kick them to the login page
        if not session.get('is_admin'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# 🔑 1. The Admin Login Page (The Gate)
# ---------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        entered_key = request.form.get("admin_key")
        master_key = os.getenv("ADMIN_SECRET")

        # Enterprise Check: Does the key match the Vault?
        if entered_key == master_key:
            session['is_admin'] = True  # ✅ Stamp the session
            flash("Welcome back, Commander.", "success")
            return redirect(url_for('admin.admin_panel'))
        else:
            flash("🚫 Access Denied: Incorrect Key.", "error")
            return redirect(url_for('admin.admin_login'))

    return render_template("admin/admin_login.html")

# ---------------------------------------------------------
# 🚪 2. Admin Logout
# ---------------------------------------------------------
@admin_bp.route("/logout")
def admin_logout():
    session.pop('is_admin', None) # Remove the stamp
    flash("Session Closed.", "info")
    return redirect(url_for('admin.admin_login'))

# ---------------------------------------------------------
# 📊 3. The Main Dashboard (Protected)
# ---------------------------------------------------------
@admin_bp.route("/")
@admin_required
def admin_panel():
    # Fetch Stats
    total_users = User.query.count()
    total_listings = Listing.query.count()
    pending_listings = Listing.query.filter_by(is_verified=False).count()
    
    users = User.query.all()
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    
    return render_template("admin/admin.html", 
                           stats={
                               "users": total_users,
                               "listings": total_listings,
                               "pending": pending_listings
                           },
                           users=users,
                           listings=listings)

# ---------------------------------------------------------
# ✅ 4. Actions (Verify/Delete)
# ---------------------------------------------------------
@admin_bp.route("/verify/<int:listing_id>")
@admin_required
def verify_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    listing.is_verified = True
    db.session.commit()
    flash(f"✅ Verified '{listing.title}'!", "success")
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route("/delete_listing/<int:listing_id>")
@admin_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    flash(f"🗑 Deleted '{listing.title}'.", "warning")
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route("/delete_user/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"👤 User {user.name} deleted.", "success")
    return redirect(url_for('admin.admin_panel'))