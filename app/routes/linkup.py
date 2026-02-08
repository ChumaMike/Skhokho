from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Service

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
            latitude=float(request.form.get('location_lat')),
            longitude=float(request.form.get('location_lng'))
        )
        db.session.add(new_service)
        db.session.commit()
        flash("Service Registered.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        
    return redirect(url_for('linkup.map_view'))