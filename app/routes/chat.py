from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.services.ai_service import get_skhokho_response

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def chat_interface():
    """Renders the main chat page."""
    return render_template('chat.html')

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """API Endpoint to process messages."""
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get response from Gemini
    bot_reply = get_skhokho_response(user_message)
    
    return jsonify({'reply': bot_reply})