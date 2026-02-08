from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import BalaaHistory, DiaryEntry
from datetime import datetime
from collections import defaultdict

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

# ✅ HELPER: Groups entries by date (Required for your new template)
def group_entries_by_date(entries):
    grouped = defaultdict(list)
    for entry in entries:
        # Format: "08 Feb 2026"
        date_key = entry.created_at.strftime("%d %b %Y")
        grouped[date_key].append(entry)
    return dict(sorted(grouped.items(), reverse=True))

@tools_bp.route('/balaa', methods=['GET', 'POST'])
@login_required
def balaa():
    # ... (Keep existing Balaa code exactly as is) ...
    result = None
    if request.method == 'POST':
        try:
            fare = float(request.form['fare'])
            group_size = int(request.form['group_size'])
            amounts_raw = request.form.get('amounts', '')
            if ',' in amounts_raw:
                amounts = [float(x) for x in amounts_raw.split(',') if x.strip()]
            else:
                amounts = [float(amounts_raw)] if amounts_raw.strip() else []
            
            expected = fare * group_size
            received = sum(amounts)
            
            new_entry = BalaaHistory(
                user_id=current_user.id,
                fare=fare,
                group_size=group_size,
                amounts=amounts_raw,
                expected=expected,
                received=received,
                change=received - expected
            )
            db.session.add(new_entry)
            db.session.commit()
            result = {'expected': expected, 'received': received, 'change': received - expected}
        except ValueError:
            flash("Invalid numbers.", "danger")

    history = BalaaHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('tools/balaa.html', result=result, history=history)

@tools_bp.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    if request.method == 'POST':
        # ✅ FIX: Get 'entry_type' instead of 'title'
        entry_type = request.form.get('entry_type', 'Thought')
        content = request.form.get('content', '').strip()
        
        if content:
            entry = DiaryEntry(
                user_id=current_user.id, 
                entry_type=entry_type,  # Saving the category
                content=content,
                created_at=datetime.utcnow()
            )
            db.session.add(entry)
            db.session.commit()
            flash("Log encrypted & saved.", "success")
            
        return redirect(url_for('tools.diary'))

    # ✅ FIX: Fetch and Group
    entries_list = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.created_at.desc()).all()
    grouped_entries = group_entries_by_date(entries_list)
    
    return render_template('tools/diary.html', entries=grouped_entries)