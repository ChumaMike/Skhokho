from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Goal, Milestone
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

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
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template('goals_dashboard.html', goals=active_goals)

# 2. Detail View: Manage Milestones for a specific Goal
@goals_bp.route('/<int:goal_id>', methods=['GET', 'POST'])
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
    
    return render_template('goal_detail.html', goal=goal)

# 3. Toggle Milestone Status
@goals_bp.route('/milestone/<int:id>/toggle')
@login_required
def toggle_milestone(id):
    milestone = Milestone.query.get_or_404(id)
    if milestone.goal.user_id != current_user.id:
        return "Unauthorized", 403
    
    milestone.is_completed = not milestone.is_completed
    db.session.commit()
    return redirect(url_for('goals.view_goal', goal_id=milestone.goal.id))

# 4. Delete/Archive Goal
@goals_bp.route('/<int:id>/delete')
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id == current_user.id:
        db.session.delete(goal)
        db.session.commit()
        flash("Objective terminated.", "info")
    return redirect(url_for('goals.dashboard'))