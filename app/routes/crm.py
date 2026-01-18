from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Contact, Interaction
from datetime import datetime, timedelta

crm_bp = Blueprint('crm', __name__, url_prefix='/network')

# 1. Network Dashboard: See all contacts
@crm_bp.route('/', methods=['GET', 'POST'])
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
                last_contacted=datetime.utcnow() # Assume we just met them
            )
            db.session.add(new_contact)
            db.session.commit()
            flash(f"Asset '{name}' added to network.", "success")
        else:
            flash("Name required.", "warning")

    # Get contacts
    contacts = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.name).all()
    return render_template('crm_dashboard.html', contacts=contacts, now=datetime.utcnow())

# 2. Dossier View: See history with one person
@crm_bp.route('/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def view_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != current_user.id:
        return "Access Denied", 403

    if request.method == 'POST':
        # Log an interaction (Call, Coffee, etc.)
        description = request.form.get('description')
        type_ = request.form.get('type')
        date_str = request.form.get('date')
        
        if description:
            # If date provided, use it, else use now
            interaction_date = datetime.utcnow()
            if date_str:
                interaction_date = datetime.strptime(date_str, '%Y-%m-%d')

            log = Interaction(
                description=description,
                interaction_type=type_,
                completed_date=interaction_date,
                is_completed=True,
                contact_id=contact.id
            )
            
            # UPDATE the contact's "last_contacted" field automatically
            contact.last_contacted = interaction_date
            
            db.session.add(log)
            db.session.commit()
            flash("Interaction logged. Network strength updated.", "success")

    return render_template('contact_detail.html', contact=contact)

# 3. Delete Contact
@crm_bp.route('/<int:id>/burn')
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id == current_user.id:
        db.session.delete(contact)
        db.session.commit()
        flash("Contact burned.", "info")
    return redirect(url_for('crm.dashboard'))