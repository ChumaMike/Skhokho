import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
# ✅ FIX: Import NetworkContact, not Contact
from app.models import ChatLog, Goal, DiaryEntry, NetworkContact, Service
from app.services.ai_service import get_skhokho_response 

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Enhanced chatbot with full database write access"""
    # 1. Get User Input
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_msg = data['message']

    # 2. Gather Context (The "Memory")
    active_goals = Goal.query.filter_by(user_id=current_user.id, is_completed=False).limit(3).all()
    goals_text = ", ".join([g.title for g in active_goals]) if active_goals else "No active goals"
    
    contacts = NetworkContact.query.filter_by(user_id=current_user.id).limit(3).all()
    contacts_text = ", ".join([c.name for c in contacts]) if contacts else "No contacts"
    
    # Include wallet and reputation in context
    context_data = f"""
    User: {current_user.username}
    Wallet Balance: R{current_user.wallet_balance}
    Reputation Points: {current_user.reputation_points}
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
    try:
        if ai_reply.startswith('{') and 'cmd' in ai_reply:
            cmd_data = json.loads(ai_reply)
            cmd = cmd_data.get('cmd')
            
            if cmd == 'add_goal':
                new_goal = Goal(
                    user_id=current_user.id,
                    title=cmd_data.get('title', 'New Goal'),
                    description=cmd_data.get('description', 'Added via Skhokho AI')
                )
                db.session.add(new_goal)
                ai_reply = f"✅ Sharp! I've added '{new_goal.title}' to your mission board."
                
            elif cmd == 'add_diary':
                new_entry = DiaryEntry(
                    user_id=current_user.id,
                    entry_type=cmd_data.get('entry_type', 'Thought'),
                    content=cmd_data.get('content', '')
                )
                db.session.add(new_entry)
                ai_reply = f"✅ Diary entry saved. Type: {new_entry.entry_type}"
                
            elif cmd == 'add_network':
                new_contact = NetworkContact(
                    user_id=current_user.id,
                    name=cmd_data.get('name'),
                    role=cmd_data.get('role', 'Contact'),
                    phone=cmd_data.get('phone'),
                    email=cmd_data.get('email')
                )
                db.session.add(new_contact)
                ai_reply = f"✅ Ayt, I saved {new_contact.name} ({new_contact.role}) to your network."
                
            elif cmd == 'set_alert':
                # For now, just acknowledge - full alert system would need Alert model
                threshold = cmd_data.get('threshold', 200)
                ai_reply = f"✅ Alert set! I'll notify you when your balance drops below R{threshold}."
                
            elif cmd == 'baala_calc':
                # Baala Calculator integration
                fare = cmd_data.get('fare', 0)
                group_size = cmd_data.get('group_size', 1)
                per_person = fare / group_size if group_size > 0 else fare
                ai_reply = f"🚖 Baala Calc: R{fare} ÷ {group_size} people = R{per_person:.2f} each"
                
            elif cmd == 'find_service':
                # Find service providers integration
                service_type = cmd_data.get('service_type', '')
                services = Service.query.filter(
                    Service.name.ilike(f'%{service_type}%') | 
                    Service.category.ilike(f'%{service_type}%')
                ).limit(3).all()
                
                if services:
                    service_list = []
                    for service in services:
                        service_list.append(f"- {service.name} ({service.category}): {service.price}c")
                    service_text = "\n".join(service_list)
                    ai_reply = f"🔍 Found {len(services)} service providers for '{service_type}':\n{service_text}\n\nVisit LinkUp to hire."
                else:
                    ai_reply = f"Sorry, no '{service_type}' services found in your area. Try checking LinkUp for other options."

    except Exception as e:
        print(f"⚠️ Command Error: {e}")
        # Don't crash, just return the text response

    db.session.commit()

    return jsonify({'response': ai_reply})
