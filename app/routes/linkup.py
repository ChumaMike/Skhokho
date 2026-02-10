from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Service, Job, User, JobChat, NetworkContact, NetworkAlert
from datetime import datetime

linkup_bp = Blueprint('linkup', __name__, url_prefix='/linkup')

@linkup_bp.route('/network')
@login_required
def network_view():
    contacts = NetworkContact.query.filter_by(user_id=current_user.id).all()
    alerts = NetworkAlert.query.filter_by(user_id=current_user.id).all()
    return render_template('network.html', contacts=contacts, alerts=alerts)

@linkup_bp.route('/network/add_contact', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name')
    if name:
        new_contact = NetworkContact(
            user_id=current_user.id,
            name=name,
            role=request.form.get('role'),
            phone=request.form.get('phone'),
            email=request.form.get('email')
        )
        db.session.add(new_contact)
        db.session.commit()
        flash("Contact Added.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/edit_contact/<int:contact_id>', methods=['POST'])
@login_required
def edit_contact(contact_id):
    contact = NetworkContact.query.get(contact_id)
    if contact and contact.user_id == current_user.id:
        contact.name = request.form.get('name')
        contact.role = request.form.get('role')
        contact.phone = request.form.get('phone')
        contact.email = request.form.get('email')
        db.session.commit()
        flash("Contact Updated.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/delete_contact/<int:contact_id>')
@login_required
def delete_contact(contact_id):
    contact = NetworkContact.query.get(contact_id)
    if contact and contact.user_id == current_user.id:
        # Delete all alerts associated with this contact
        NetworkAlert.query.filter_by(contact_id=contact_id).delete()
        db.session.delete(contact)
        db.session.commit()
        flash("Contact Deleted.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/add_alert/<int:contact_id>', methods=['POST'])
@login_required
def add_alert(contact_id):
    contact = NetworkContact.query.get(contact_id)
    if contact and contact.user_id == current_user.id:
        title = request.form.get('alert_title')
        if title:
            alert_date = None
            if request.form.get('alert_date'):
                alert_date = datetime.strptime(request.form.get('alert_date'), '%Y-%m-%dT%H:%M')
            
            new_alert = NetworkAlert(
                user_id=current_user.id,
                contact_id=contact_id,
                title=title,
                description=request.form.get('alert_description'),
                alert_type=request.form.get('alert_type', 'Email'),
                alert_date=alert_date,
                is_completed=False
            )
            db.session.add(new_alert)
            db.session.commit()
            flash("Alert Added.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/edit_alert/<int:alert_id>', methods=['POST'])
@login_required
def edit_alert(alert_id):
    alert = NetworkAlert.query.get(alert_id)
    if alert and alert.user_id == current_user.id:
        alert.title = request.form.get('alert_title')
        alert.description = request.form.get('alert_description')
        alert.alert_type = request.form.get('alert_type')
        if request.form.get('alert_date'):
            alert.alert_date = datetime.strptime(request.form.get('alert_date'), '%Y-%m-%dT%H:%M')
        db.session.commit()
        flash("Alert Updated.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/delete_alert/<int:alert_id>')
@login_required
def delete_alert(alert_id):
    alert = NetworkAlert.query.get(alert_id)
    if alert and alert.user_id == current_user.id:
        db.session.delete(alert)
        db.session.commit()
        flash("Alert Deleted.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/network/toggle_alert/<int:alert_id>')
@login_required
def toggle_alert(alert_id):
    alert = NetworkAlert.query.get(alert_id)
    if alert and alert.user_id == current_user.id:
        alert.is_completed = not alert.is_completed
        db.session.commit()
        flash("Alert Status Updated.", "success")
    return redirect(url_for('linkup.network_view'))

@linkup_bp.route('/')
@login_required
def economy_view():
    services = Service.query.all()
    return render_template('linkup.html', services=services)

@linkup_bp.route('/map')
@login_required
def map_view():
    return render_template('linkup/map.html')

@linkup_bp.route('/join', methods=['POST'])
@login_required
def join_economy():
    try:
        print("Form data:", request.form)
        new_service = Service(
            provider_id=current_user.id,
            name=request.form.get('service_name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            price=int(request.form.get('price', 50)), # Default 50 credits
            latitude=float(request.form.get('location_lat', 0)),
            longitude=float(request.form.get('location_lng', 0))
        )
        db.session.add(new_service)
        db.session.commit()
        print("Created service:", new_service)
        print("All services:", Service.query.all())
        flash("Service Registered.", "success")
    except Exception as e:
        print("Error:", str(e))
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for('linkup.economy_view'))

# 💰 THE TRANSACTION ROUTE
@linkup_bp.route('/hire/<int:service_id>', methods=['POST'])
@login_required
def hire_provider(service_id):
    service = Service.query.get_or_404(service_id)
    
    # 1. Check Funds
    print(f"Current user: {current_user.username}, Wallet: {current_user.wallet_balance}, Service Price: {service.price}, Current user ID: {current_user.id}")
    if current_user.wallet_balance < service.price:
        flash(f"Insufficient Credits. Need {service.price}.", "error")
        return redirect(url_for('linkup.map_view'))
    
    # 2. Deduct & Lock (Escrow)
    current_user.wallet_balance -= service.price
    
    # 3. Create Job
    new_job = Job(
        client_id=current_user.id,
        provider_id=service.provider_id,
        service_id=service.id,
        status="In_Progress",
        price=service.price,
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    flash("Job Started! Credits held in escrow.", "success")
    return redirect(url_for('linkup.view_job', job_id=new_job.id))

# 💬 THE CHAT ROUTES
@linkup_bp.route('/job/<int:job_id>')
@login_required
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    # Security: Only participants can view
    if current_user.id not in [job.client_id, job.provider_id]:
        flash("Unauthorized access.", "error")
        return redirect(url_for('linkup.map_view'))
        
    return render_template('job_chat.html', job=job)

@linkup_bp.route('/chat/send', methods=['POST'])
@login_required
def send_chat():
    job_id = request.form.get('job_id')
    content = request.form.get('message')
    
    if job_id and content:
        # Create a new chat message
        chat_message = JobChat(
            job_id=job_id,
            sender_id=current_user.id,
            message=content
        )
        db.session.add(chat_message)
        db.session.commit()
    
    return redirect(url_for('linkup.view_job', job_id=job_id))
