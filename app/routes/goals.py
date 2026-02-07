from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Goal
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

# 1. Dashboard (List Goals)
@goals_bp.route('/')
@login_required
def dashboard():
    # Only show INCOMPLETE goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).all()
    return render_template('goals.html', goals=active_goals)

# 2. Add Goal (The missing link!)
@goals_bp.route('/add', methods=['POST'])
@login_required
def add_goal():
    title = request.form.get('title')
    description = request.form.get('description')
    
    if title:
        new_goal = Goal(
            title=title, 
            description=description,
            user_id=current_user.id,
            created_at=datetime.utcnow(),
            is_completed=False
        )
        db.session.add(new_goal)
        db.session.commit()
        flash("Mission Initialized.", "success")
        
    return redirect(url_for('goals.dashboard'))

# 3. Complete Goal
@goals_bp.route('/complete/<int:goal_id>')
@login_required
def complete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    # Security Check: Is this MY goal?
    if goal.user_id != current_user.id:
        flash("Access Denied.", "error")
        return redirect(url_for('goals.dashboard'))
        
    goal.is_completed = True
    db.session.commit()
    flash("Mission Accomplished.", "success")
    
    return redirect(url_for('goals.dashboard'))