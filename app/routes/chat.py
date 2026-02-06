import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
# ✅ FIX 1: Correct Import Spelling (ChatLog, not Chatlog)
from app.models import ChatLog, Goal, DiaryEntry, Contact 
from app.services.ai_service import get_skhokho_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json()
        user_message = data.get('message')
        
        # 1. Context
        active_goals = Goal.query.filter_by(user_id=current_user.id).limit(3).all()
        goals_text = ", ".join([g.title for g in active_goals]) if active_goals else "None"
        context = f"User's Current Goals: {goals_text}"
        
        # 2. AI Brain
        ai_response_text = get_skhokho_response(user_message, context)
        
        # Default reply is just the text
        final_reply = ai_response_text
        
        # 3. Check for JSON Commands
        if ai_response_text.strip().startswith("{") and "cmd" in ai_response_text:
            try:
                command = json.loads(ai_response_text)
                
                if command['cmd'] == 'add_goal':
                    new_item = Goal(title=command['title'], description="AI Generated", user_id=current_user.id)
                    db.session.add(new_item)
                    final_reply = f"Sho! Goal set: '{command['title']}'."
                    
                elif command['cmd'] == 'add_diary':
                    new_item = DiaryEntry(entry_type="AI Log", content=f"{command['title']}: {command['content']}", user_id=current_user.id)
                    db.session.add(new_item)
                    final_reply = f"Sharp. Logged in Diary: '{command['title']}'."
                    
                elif command['cmd'] == 'add_network':
                    new_item = Contact(name=command['name'], role=command['category'], user_id=current_user.id)
                    db.session.add(new_item)
                    final_reply = f"Network updated. Added '{command['name']}'."
                
                db.session.commit()
                print(f"✅ ACTION SUCCESS: {command['cmd']}")
            except Exception as e:
                print(f"⚠️ ACTION FAILED: {e}")
                # Fallback: Just show the text if the DB save fails
                final_reply = "Eish, I tried to save that but the database blocked me. Check the logs."

        # 4. Save Chat History
        # Ensure ChatLog table exists!
        log = ChatLog(user_id=current_user.id, message=user_message, response=final_reply)
        db.session.add(log)
        db.session.commit()
        
        # ✅ FIX 2: Send ALL keys to prevent 'undefined'
        return jsonify({
            "response": final_reply, 
            "message": final_reply,
            "reply": final_reply,
            "status": "success"
        })

    except Exception as e:
        print(f"❌ CRITICAL CHAT ERROR: {e}")
        return jsonify({"response": "System Error. Check Terminal.", "message": "System Error."}), 500