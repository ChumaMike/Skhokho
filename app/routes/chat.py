from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_service import get_skhokho_response
from app.models import Goal, Contact, BalaaHistory # <--- Import your models

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def chat_interface():
    # We are using the main dashboard as the chat interface now, 
    # but we keep this route just in case you access /chat directly.
    return render_template('index.html')

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # --- 1. GATHER SYSTEM INTELLIGENCE ---
    
    # A. Get Active Goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, completed=False).all()
    if active_goals:
        goals_text = "\n".join([f"- {g.title}: {g.progress}% Complete" for g in active_goals])
    else:
        goals_text = "No active missions. User is drifting."

    # B. Get Financial Context (Last Balaa Trip)
    last_trip = BalaaHistory.query.filter_by(user_id=current_user.id).order_by(BalaaHistory.created_at.desc()).first()
    if last_trip:
        balaa_text = f"Last taxi calculation: Collected R{last_trip.received} vs Expected R{last_trip.expected}."
    else:
        balaa_text = "No financial data recorded yet."

    # C. Construct the "Context Packet"
    system_context = f"""
    USER IDENTITY: {current_user.username}
    
    CURRENT MISSION STATUS (GOALS):
    {goals_text}
    
    RECENT FINANCIAL LOG:
    {balaa_text}
    """

    # --- 2. SEND TO BRAIN WITH CONTEXT ---
    # We pass the system_context to the AI service
    bot_reply = get_skhokho_response(user_message, context_data=system_context)
    
    return jsonify({'reply': bot_reply})