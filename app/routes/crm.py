from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Contact, Interaction
from datetime import datetime

# URL Prefix is handled in __init__.py (/network)
crm_bp = Blueprint('crm', __name__)

# 1. Network Dashboard: See all contacts
@crm_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Adding a new Contact
        name = request.form.get('name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if name:
            new_contact = Contact(
                name=name,
                role=role,
                email=email,
                phone=phone,
                user_id=current_user.id,
                last_contacted=datetime.utcnow()
            )
            db.session.add(new_contact)
            db.session.commit()
            flash(f"Asset '{name}' added to network.", "success")
        else:
            flash("Name required.", "warning")

    # Get contacts
    contacts = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.name).all()
    return render_template('crm.html', contacts=contacts, now=datetime.utcnow())