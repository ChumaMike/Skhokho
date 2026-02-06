from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import BalaaHistory, DiaryEntry
from datetime import datetime
from collections import defaultdict

# URL Prefix is handled in __init__.py (/tools)
tools_bp = Blueprint('tools', __name__)

# Helper for Diary
def group_entries_by_date(entries):
    grouped = defaultdict(list)
    for entry in entries:
        date = entry.timestamp.strftime("%Y-%m-%d")
        grouped[date].append(entry)
    return dict(sorted(grouped.items(), reverse=True))

@tools_bp.route('/balaa', methods=['GET', 'POST'])
@login_required
def balaa():
    result = None
    if request.method == 'POST':
        try:
            fare = float(request.form['fare'])
            group_size = int(request.form['group_size'])
            amounts = [float(a) for a in request.form.getlist('amounts') if a.strip()]
            
            expected = fare * group_size
            received = sum(amounts)
            
            # Save to DB
            new_entry = BalaaHistory(
                user_id=current_user.id,
                fare=fare,
                group_size=group_size,
                amounts=','.join(map(str, amounts)),
                expected=expected,
                received=received,
                change=received - expected
            )
            db.session.add(new_entry)
            db.session.commit()
            
            result = {
                'expected': expected,
                'received': received,
                'change': received - expected
            }
        except ValueError:
            flash("Invalid numbers entered.", "danger")

    history = BalaaHistory.query.filter_by(user_id=current_user.id)\
        .order_by(BalaaHistory.created_at.desc()).all()
    
    return render_template('balaa.html', result=result, history=history)

@tools_bp.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        entry_type = request.form.get('entry_type')
        
        if content and entry_type:
            entry = DiaryEntry(user_id=current_user.id, entry_type=entry_type, content=content)
            db.session.add(entry)
            db.session.commit()
            flash("Saved!", "success")
        else:
            flash("Cannot save empty entry.", "warning")

    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.timestamp.desc()).all()
    return render_template('diary.html', entries=group_entries_by_date(entries))