from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Goal

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goals_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch Data
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=True).all()
    return render_template('goals.html', active_goals=active_goals, completed_goals=completed_goals)

# ✅ FIX: Create the dedicated 'add_goal' route
@goals_bp.route('/add', methods=['POST'])
@login_required
def add_goal():
    title = request.form.get('title')
    if title:
        new_goal = Goal(
            user_id=current_user.id,
            title=title,
            description=request.form.get('description'),
            is_completed=False
        )
        db.session.add(new_goal)
        db.session.commit()
        flash("Mission Added.", "success")
    return redirect(url_for('goals.dashboard'))

@goals_bp.route('/complete/<int:goal_id>')
@login_required
def complete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal and goal.user_id == current_user.id:
        goal.is_completed = True
        db.session.commit()
        flash("Mission Accomplished!", "success")
    return redirect(url_for('goals.dashboard'))