from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Goal, Milestone
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goals_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch Data
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=True).all()
    return render_template('goals.html', active_goals=active_goals, completed_goals=completed_goals)

@goals_bp.route('/strategic')
@login_required
def strategic_dashboard():
    goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).all()
    return render_template('goals_dashboard.html', goals=goals)

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

@goals_bp.route('/strategic/add', methods=['POST'])
@login_required
def add_strategic_goal():
    title = request.form.get('title')
    if title:
        target_date = None
        if request.form.get('target_date'):
            target_date = datetime.strptime(request.form.get('target_date'), '%Y-%m-%d')
        
        new_goal = Goal(
            user_id=current_user.id,
            title=title,
            description=request.form.get('description'),
            category=request.form.get('category', 'Personal'),
            target_date=target_date,
            progress=0,
            is_completed=False
        )
        db.session.add(new_goal)
        db.session.commit()
        flash("Strategic Objective Initiated.", "success")
    return redirect(url_for('goals.strategic_dashboard'))

@goals_bp.route('/view/<int:goal_id>')
@login_required
def view_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal and goal.user_id == current_user.id:
        return render_template('goal_detail.html', goal=goal)
    else:
        flash("Goal not found.", "error")
        return redirect(url_for('goals.strategic_dashboard'))

@goals_bp.route('/delete/<int:goal_id>')
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal and goal.user_id == current_user.id:
        # Delete all milestones associated with this goal
        Milestone.query.filter_by(goal_id=goal_id).delete()
        db.session.delete(goal)
        db.session.commit()
        flash("Objective Terminated.", "success")
    return redirect(url_for('goals.strategic_dashboard'))

@goals_bp.route('/complete/<int:goal_id>')
@login_required
def complete_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal and goal.user_id == current_user.id:
        goal.is_completed = True
        db.session.commit()
        flash("Mission Accomplished!", "success")
    return redirect(url_for('goals.dashboard'))

@goals_bp.route('/toggle_milestone/<int:milestone_id>')
@login_required
def toggle_milestone(milestone_id):
    milestone = Milestone.query.get(milestone_id)
    if milestone and milestone.goal.user_id == current_user.id:
        milestone.is_completed = not milestone.is_completed
        db.session.commit()
        
        # Recalculate goal progress based on completed milestones
        goal = milestone.goal
        total_milestones = len(goal.milestones)
        if total_milestones > 0:
            completed_milestones = len([m for m in goal.milestones if m.is_completed])
            goal.progress = int((completed_milestones / total_milestones) * 100)
            # Auto-complete goal if all milestones are completed
            if goal.progress == 100:
                goal.is_completed = True
            db.session.commit()
    return redirect(url_for('goals.view_goal', goal_id=milestone.goal.id))

@goals_bp.route('/add_milestone/<int:goal_id>', methods=['POST'])
@login_required
def add_milestone(goal_id):
    goal = Goal.query.get(goal_id)
    if goal and goal.user_id == current_user.id:
        title = request.form.get('milestone_title')
        if title:
            new_milestone = Milestone(
                goal_id=goal_id,
                title=title,
                is_completed=False
            )
            db.session.add(new_milestone)
            db.session.commit()
            flash("Sub-Task Added.", "success")
    return redirect(url_for('goals.view_goal', goal_id=goal_id))
