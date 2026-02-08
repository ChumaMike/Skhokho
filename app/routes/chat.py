import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
# ✅ FIX: Import NetworkContact, not Contact
from app.models import ChatLog, Goal, DiaryEntry, NetworkContact
from app.services.ai_service import get_skhokho_response 

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    # 1. Get User Input
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_msg = data['message']

    # 2. Gather Context (The "Memory")
    # We feed Skhokho the user's current goals and contacts so it can give specific advice.
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).limit(3).all()
    goals_text = ", ".join([g.title for g in active_goals]) if active_goals else "No active goals"
    
    # ✅ FIX: Use NetworkContact here
    contacts = NetworkContact.query.filter_by(user_id=current_user.id).limit(3).all()
    contacts_text = ", ".join([c.name for c in contacts]) if contacts else "No contacts"

    context_data = f"""
    User: {current_user.username}
    Current Goals: {goals_text}
    Key Contacts: {contacts_text}
    """

    # 3. Get AI Response
    ai_reply = get_skhokho_response(user_msg, context_data)

    # 4. Save Conversation
    log = ChatLog(
        user_id=current_user.id,
        message=user_msg,
        response=ai_reply
    )
    db.session.add(log)
    
    # 5. Execute Commands (If AI returned a JSON command)
    # Example: If AI said {"cmd": "add_goal", ...}, we do it here.
    try:
        if ai_reply.startswith('{') and 'cmd' in ai_reply:
            cmd_data = json.loads(ai_reply)
            
            if cmd_data.get('cmd') == 'add_goal':
                new_goal = Goal(
                    user_id=current_user.id,
                    title=cmd_data.get('title', 'New Goal'),
                    description="Added via Macalaa AI"
                )
                db.session.add(new_goal)
                ai_reply = f"Sharp. I've added '{new_goal.title}' to your mission board."
                
            elif cmd_data.get('cmd') == 'add_network':
                new_contact = NetworkContact(
                    user_id=current_user.id,
                    name=cmd_data.get('name'),
                    role=cmd_data.get('category', 'Contact')
                )
                db.session.add(new_contact)
                ai_reply = f"Ayt, I saved {new_contact.name} to your network."

    except Exception as e:
        print(f"⚠️ Command Error: {e}")
        # Don't crash, just return the text response

    db.session.commit()

    return jsonify({'response': ai_reply})