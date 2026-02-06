from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Goal, Milestone
from datetime import datetime

# URL Prefix is handled in __init__.py (/goals)
goals_bp = Blueprint('goals', __name__)

# 1. Dashboard: View all high-level goals
@goals_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        target_date_str = request.form.get('target_date')
        
        if title:
            target_date = None
            if target_date_str:
                try:
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                except ValueError:
                    flash("Invalid date format", "danger")
            
            new_goal = Goal(
                title=title, 
                category=category, 
                description=description, 
                target_date=target_date, 
                user_id=current_user.id
            )
            db.session.add(new_goal)
            db.session.commit()
            flash("New objective initialized.", "success")
        else:
            flash("Objective title required.", "warning")
            
    # Get active goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='Active').all()
    return render_template('goals.html', goals=active_goals)

# 2. Detail View: Manage Milestones for a specific Goal
@goals_bp.route('/view/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def view_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    # Security: Ensure user owns this goal
    if goal.user_id != current_user.id:
        flash("Access Denied.", "danger")
        return redirect(url_for('goals.dashboard'))

    if request.method == 'POST':
        # Adding a new Milestone
        title = request.form.get('milestone_title')
        if title:
            milestone = Milestone(title=title, goal_id=goal.id)
            db.session.add(milestone)
            db.session.commit()
            flash("Milestone added.", "success")
    
    return render_template('view_goal.html', goal=goal)