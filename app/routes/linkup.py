from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Service, Job, JobChat, User
from datetime import datetime

linkup_bp = Blueprint('linkup', __name__, url_prefix='/linkup')

@linkup_bp.route('/')
@login_required
def map_view():
    services = Service.query.all()
    return render_template('linkup.html', services=services)

@linkup_bp.route('/join', methods=['POST'])
@login_required
def join_economy():
    try:
        new_service = Service(
            user_id=current_user.id,
            name=request.form.get('service_name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            cost=int(request.form.get('cost', 50)), # Default 50 credits
            latitude=float(request.form.get('location_lat', 0)),
            longitude=float(request.form.get('location_lng', 0))
        )
        db.session.add(new_service)
        db.session.commit()
        flash("Service Registered.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for('linkup.map_view'))

# 💰 THE TRANSACTION ROUTE
@linkup_bp.route('/hire/<int:service_id>', methods=['POST'])
@login_required
def hire_provider(service_id):
    service = Service.query.get_or_404(service_id)
    
    # 1. Check Funds
    if current_user.wallet_balance < service.cost:
        flash(f"Insufficient Credits. Need {service.cost}.", "error")
        return redirect(url_for('linkup.map_view'))
    
    # 2. Deduct & Lock (Escrow)
    current_user.wallet_balance -= service.cost
    
    # 3. Create Job
    new_job = Job(
        customer_id=current_user.id,
        provider_id=service.user_id,
        service_id=service.id,
        status="In_Progress",
        agreed_price=service.cost,
        is_paid=False # Money is in escrow
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
    if current_user.id not in [job.customer_id, job.provider_id]:
        flash("Unauthorized access.", "error")
        return redirect(url_for('linkup.map_view'))
        
    return render_template('job_chat.html', job=job)

@linkup_bp.route('/chat/send', methods=['POST'])
@login_required
def send_chat():
    job_id = request.form.get('job_id')
    content = request.form.get('message')
    
    if job_id and content:
        msg = JobChat(
            job_id=job_id,
            sender_id=current_user.id,
            message=content,
            timestamp=datetime.utcnow()
        )
        db.session.add(msg)
        db.session.commit()
        
    return redirect(url_for('linkup.view_job', job_id=job_id))