from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_service import get_skhokho_response
from app.models import Goal, Contact  # <--- Import your models

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def chat_interface():
    return render_template('index.html') # Reusing index since we moved chat there

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # --- 1. GATHER INTELLIGENCE ---
    # Get active goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, completed=False).all()
    goals_text = ", ".join([f"{g.title} ({g.progress}%)" for g in active_goals]) if active_goals else "No active goals."

    # Get cold contacts (people ignored for > 30 days)
    # (Assuming you have a helper for this, or just fetching all for now)
    contacts_count = Contact.query.filter_by(user_id=current_user.id).count()

    # Create a "Context Packet" to send to the brain
    system_context = f"""
    USER DATA:
    - Username: {current_user.username}
    - Active Goals: {goals_text}
    - Total Network Contacts: {contacts_count}
    """

    # --- 2. SEND TO BRAIN WITH CONTEXT ---
    bot_reply = get_skhokho_response(user_message, system_context)
    
    return jsonify({'reply': bot_reply})